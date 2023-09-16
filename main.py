import os, time, argparse, re
import zipfile
from Files import Files, STD, Settings
from Drive import Drive
from Zip   import zip
from Audio import Audio


THIS_DIRECTORY   = Files.newPath(os.path.dirname(os.path.realpath(__file__)))
CREDENTIALS_FILE = THIS_DIRECTORY / "credentials.json"

def upload_log_files(drive, settings):
    log_folder_id = settings.json["drive_ids"]["logs"]
    lof_record_location = Files.newPath( settings.json["local_paths"]["logs"] )

    # get list of wav files
    wav_files = Files.lsFiles(lof_record_location, suffix="wav")

    # convert to mp3
    Audio.wavToMP3(wav_files)

    # create new folder on drive for log files
    folder_id = drive.create_folder(Drive.get_current_date(), log_folder_id)

    # get list of new mp3 files
    mp3_files = Files.lsFiles(lof_record_location, suffix="mp3")

    # upload the mp3's to the cloud
    drive.upload_files(mp3_files, folder_id)

def clean_log_folder(settings):
    lof_record_location = Files.newPath( settings.json["local_paths"]["logs"] )
    Files.removeAll(Files.ls(lof_record_location), confirm=False)
    print("\n--> Log folder cleaned!\n")

def open_for_practice():
    # stop fancy window program
    os.system("yabai --stop-service")

    # Switch MAC output to different output
    os.system("SwitchAudioSource -u BlackHole2ch_UID")
    #  {"name": "BlackHole 2ch", "type": "input", "id": "97", "uid": "BlackHole2ch_UID"}
    #  {"name": "SoundDesk Virtual Driver", "type": "output", "id": "114", "uid": "SoundDesk_UID"}
    time.sleep(2)
    
    #  # open Bome Midi
    #  os.system('open "/Users/mitch/Documents/LOF/Bome/SoundDesk_Update_230828.bmtp"')
    #  time.sleep(2)

    #  # open Stems Desk
    #  os.system('open "/Users/mitch/Documents/LOF/SoundDesk/StemRecord_230824.sdsk"')
    #  time.sleep(2)

    #  # open Main Desk
    #  os.system('open "/Users/mitch/Documents/LOF/SoundDesk/Main_230823.sdsk"')
    #  time.sleep(2)

    #  open Reaper
    os.system('open "/Applications/REAPER.app"')
    time.sleep(2)

    # open ableton
    #  os.system('open "/Applications/Ableton\ Live\ 11\ Standard.app/"')

    # open MIDI settings
    time.sleep(5) # make sure it's on top
    os.system('open "/System/Applications/Utilities/Audio MIDI Setup.app"')

    # keep system awake
    print("--> You are now caffeinated.. press Ctrl-C to exit")
    os.system('caffeinate')


def upload_stems_and_project_files(drive, settings, days=None):
    # Process
    # - zip all project files
    # - get list of all project names
    # - iterate through projects
    #   - if project starts with MXR_ then add upload to mixer_projects
    #   - else
    #   - add upload of all audio files inside stems except master to the
    #     stems subdirectory on drive
    #   - create mp3 version and add upload of master audio files to bounces
    #     subdirectory on drive
    #   - add mp3 path to array (to delete later)
    #   - add upload of project to reaper directory on drive
    # - upload all files
    # - remove all zip files
    # - remove all mp3 files

    upload_files   = []
    wavToMp3_files = []

    projects_path           = Files.newPath(settings.json["local_paths"]["projects"])
    mixer_projects_drive_id = settings.json["drive_ids"]["mixer_projects"]

    zip(projects_path.absolute())

    project_folders = Files.lsFolders(projects_path)

    for project_folder in project_folders:
        if days == None or Files.wasEditedWithin(project_folder, days):
            # mixer projects are treated differently
            if project_folder.stem.split("_")[0] == "MXR":
                upload_files.append([project_folder.with_suffix(".zip"), mixer_projects_drive_id])
                continue

        # song projects after this point
        if not project_folder.stem in settings.json["projects"]:
            # if project doesnt exist in settings, get or create folder on drive
            songs_id = settings.json["drive_ids"]["songs"]
            parent_id = drive.create_folder(project_folder.stem, songs_id)
            settings.json["projects"][project_folder.stem] = parent_id
            settings.save()

        parent_id  = settings.json["projects"][project_folder.stem]
        if parent_id == "DO NOT UPLOAD":
            continue
        stems_id   = drive.create_folder("Stems", parent_id)
        bounces_id = drive.create_folder("Bounces", parent_id)
        reaper_id  = drive.create_folder("Reaper", parent_id)

        #  print(f"--> Name:       {project_folder.stem}")
        #  print(f"    parent_id:  {parent_id}")
        #  print(f"    stems_id:   {stems_id}")
        #  print(f"    bounces_id: {bounces_id}")
        #  print(f"    reaper_id:  {reaper_id}")

        if days == None or Files.wasEditedWithin(project_folder, days):
            upload_files.append([project_folder.with_suffix(".zip"), reaper_id])

        stems_folder = project_folder / "Stems"
        stems = Files.lsFiles(stems_folder, suffix="wav")
        for stem in stems:
            if days == None or Files.wasEditedWithin(stem, days):
                if "Master" in stem.stem:
                    upload_files.append([stem.absolute(), bounces_id])
                    upload_files.append([stem.absolute().with_suffix(".mp3"), bounces_id])
                    wavToMp3_files.append(stem.absolute())
                else:
                    upload_files.append([stem.absolute(), stems_id])

    #  print("--> Upload Files")
    #  STD.printList(upload_files)
    #  print("--> Upload MP3s")
    #  STD.printList(wavToMp3_files)

    print("--> Converting Masters to MP3's..")
    Audio.wavToMP3(wavToMp3_files)

    print("--> Uploading to drive..")
    drive.upload_files_different_parents(upload_files)

    # remove mp3's and zip files
    print("--> Removing unused files..")
    for mp3 in wavToMp3_files:
        Files.remove(mp3.absolute().with_suffix(".mp3"), False)
    Files.removeAll( Files.lsFiles(projects_path, suffix="zip"), False )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload",              action="store_true", help="Upload all")
    parser.add_argument("--upload-projects",     action="store_true", help="Upload projects modified within 24hrs")
    parser.add_argument("--upload-all-projects", action="store_true", help="Upload all projects regardless of last modified")
    parser.add_argument("--upload-logs",         action="store_true", help="Upload logs")
    parser.add_argument("--clean",               action="store_true", help="Clean up log folder")
    parser.add_argument("--open",                action="store_true", help="Start all programs for practice")
    parser.add_argument("--open-show",           action="store_true", help="Start all programs for a show")
    parser.add_argument("--edit",                action="store_true", help="Edit the settings file")
    args = parser.parse_args()

    settings = Settings("settings.json")

    if args.open:
        ans = input("Would you like to clean the log folder?: ").lower()
        if ans == "y" or ans == "yes":
            clean_log_folder(settings)
        open_for_practice()
        print("\n--> Done!\n")
        exit()

    if args.open_show:
        #  open_for_show()
        print("\n--> Done!\n")
        exit()

    if args.edit:
        os.system(f'nvim "{settings.file.absolute()}"')
        exit()

    drive = Drive("root", CREDENTIALS_FILE)

    if args.upload or args.upload_logs:
      upload_log_files(drive, settings)

    if args.upload or args.upload_projects:
        upload_stems_and_project_files(drive, settings, days=1)

    if args.upload_all_projects:
        upload_stems_and_project_files(drive, settings)

    if args.clean:
        clean_log_folder(settings)

    print("\n--> Done!\n")
