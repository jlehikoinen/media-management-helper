Media Management Helper
=======================

Media Management Helper is part of my personal photo and video management solution. Designed mainly to help automating photo and video management with Dropbox Camera Uploads. See my photo management solution [here](http://www.trrt.me/#!./md/photo_management.md).

- Uses compiled Swift binary or  [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/) to read file metadata
- Creates directory tree based on EXIF DateTimeOriginal year and month metadata information
- Moves files from source folder to target folder(s)

Pre-requisites
--------------

- Swift binary is compiled for OS X 10.10
- exiftool 9.82+ (optional)

Usage
-----

**Git clone repo:**

`$ git clone https://github.com/jlehikoinen/media-management-helper.git`

**Edit global variables in `media_mgmt_helper.py` script.**

1. File types
2. Select Swift binary or ExifTool
3. Media folder descriptions
4. Dropbox location
5. 'Unsorted' folder location

**Run script**

If one common target folder is used for both photos and videos:

`$ ./media_mgmt_helper.py path/to/source_folder path/to/target_media`

If two separate target folders are used, one for photos and one for videos:

`$ ./media_mgmt_helper.py path/to/source_folder path/to/target_photos path/to/target_videos`

Check [Utilizing OS X LaunchAgent](#utilizing-os-x-launchagent) part for automated solution.

Additional information
----------------------

- Root target folder(s) need to exist in advance
- Script creates target folder structure automatically if needed
- Files which are missing metadata are moved to `Unsorted media files` folder
- File types which are not listed in the EXTENSIONS arrays are left in the source folder
- If no year and month information can't be read from the file, script tries to parse year and month info from file name. Carousel iOS app uses `2015-02-18 08.57.33.jpg` naming convention

Minor things:

- Tool can't handle subfolders inside source folder
- Tool doesn't check for empty source folder


Directory tree naming convention
--------------------------------

Designed mainly for Unbound iOS app folder view.

**One common target folder for both photos and videos:**

```
media_root
  |-year
      |-year-month
```

Example:

```
My Media Files
  |-2015
    |-2015-01
      2015-02
      etc.
```

**Two target folders, one for photos and one for videos:**


```
photos_root
  |-year
      |-year-month-<photos>

videos_root
  |-year
    |-year-month-<videos>
```

Example:

```
My Photos
  |-2015
    |-2015-01-photos
      2015-02-photos
      etc.

My Videos
  |-2015
    |-2015-01-videos
      2015-02-videos
      etc.
```

Utilizing OS X LaunchAgent
--------------------------

OS X LaunchD system can be used with the `media_mgmt_helper.py` script to automatically move files from source folder to target folder(s).

Edit `com.yourdomain.media_mgmt_helper.plist` file with your personal details. Make sure that source path and `WatchPaths` path match. Add two target folders, if you want to put photos and videos into separate folders.

- `media_mgmt_helper.py` location
- Source folder
- Target folder(s)
- StandardOutPath
- StandardErrorPath

Move custom LaunchAgent plist to user `LaunchAgents` folder:

`$ mv path/to/com.yourdomain.media_mgmt_helper.plist ~/Library/LaunchAgents/`

Load LaunchAgent:

`$ launchctl load ~/Library/LaunchAgents/com.yourdomain.media_mgmt_helper.plist`

Make sure that `media_mgmt_helper.py` has execute file permissions for LaunchAgent to work properly.
