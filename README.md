# LOF Upload Script

Used for uploading Reaper projects and stems to the drive.

## NEEDS

This script relies on a few custom libraries that can be found here:
- [Extra Python Libraries](https://github.com/vindennl48/dotfiles/tree/macm1/python)

You will also need the `credentials.json` and `client_secrets.json` from google
drive to be able to upload.

Lastly, this will create a settings.json file that will hold all the data for
your songs and root locations.

It should look something like this.  The `drive_ids` section holds the root 
folder id's of the parent locations.  `local_paths` refers to where the files
are stored on your local hard drive.  `projects` are the folder id's on the
drive that the projects will be saved in.  If no folder or song is specified,
a new one will be created for you in the `drive_ids:songs` location on the drive.
```
{
  "drive_ids": {
    "mixer_projects": "1dqnUpo9kpozRls9u-dw6PBs5Oi_wjk7y",
    "songs": "11IeMGGML7GwVoMiIUKu9cljMDBJ7bC0I",
    "logs": "1Im1w4ZbV5afntsWZvl4SoLZOKASw4k9J"
  },
  "local_paths": {
    "projects": "~/Documents/LOF/Reaper",
    "logs": "~/Desktop/lof_record"
  },
  "projects": {
    "Homebody": "1UvU4b0qbzsM2jX3KpU2W4Vq5ooUwi6NH",
    "Steel Yourselves": "1ykG44paOpsYwPfYHjcTsIi0U2A26LE7g",
    "Slough": "1ZX82gpzpPYBUqwAnkPVZfPYtMNHVOD2w",
    "Homebody Live": "DO NOT UPLOAD",
    "Steel Yourselves Live": "DO NOT UPLOAD",
    "Slough Live": "DO NOT UPLOAD",
    "MXR_Practice": "1kMNBHbNGZSdGRneZXRNvu05LMyk6xq1Q",
    "MXR_FX_WEEK": "1oFDsedODlkz8nMPYRSKZQ6kwRqwiyFRC"
  }
}
```
