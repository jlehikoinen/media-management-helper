Media Management Helper
=======================

Media Management Helper is part of my personal photo and video management solution. Mainly designed to help automating photo and video management with Dropbox Camera Uploads. See my photo management solution [here](http://www.trrt.me/#!./md/photo_management.md).

- Uses compiled Swift binary `get-metadata` or  [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/) to read file metadata
    - DateTimeOriginal year
    - DateTimeOriginal month
    - Camera model
- Creates directory tree based on EXIF DateTimeOriginal year and month metadata information
- Moves files from source folder to target folder(s)

Pre-requisites
--------------

- Valid photo and video metadata
- Swift binary is compiled for OS X 10.10
- exiftool 9.82+ (if used)

Usage
-----

**Git clone repo:**

`$ git clone https://github.com/jlehikoinen/media-management-helper.git`

`$ cd media-management-helper`

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

- Script can't handle subfolders inside source folder
- Script doesn't check for empty source folder

Testing Swift binary
--------------------

The Swift binary isn't quite finalized yet, but it should read all the necessary file metadata correctly. You can try out these commands separately if you need to troubleshoot something.

Get camera model information from a photo file:

`$ ./get-metadata photo Model /path/to/photo.JPG`

Get file creation date information from a photo file:

`$ ./get-metadata photo DateTimeOriginal /path/to/photo.JPG`

Get camera model information from a video file:

`$ ./get-metadata video common/model /path/to/video.MOV`

Get file creation date information from a video file:

`$ ./get-metadata video common/creationDate /path/to/video.MOV`

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

Log file sample
---------------

```
21.02.2015 19.19.54: iPad mini 2 - Moving 2015-02-21 19.17.21.jpg to 2015-02-kuvat
24.02.2015 19.33.32: NIKON 1 J1 - Moving DSC_3143.JPG to 2015-02-kuvat
25.02.2015 13.32.13: iPhone 5s - Moving 2015-02-25 13.33.59.mov to 2015-02-videot
25.02.2015 13.45.04: Moving 2015-02-25 13.46.29.jpg to 2015-02-kuvat
```

Utilizing OS X LaunchAgent
--------------------------

OS X LaunchD system can be used together with the `media_mgmt_helper.py` script to automatically move files from source folder to target folder(s).

Rename `com.yourdomain.media_mgmt_helper.plist` LaunchAgent file and add your own details to the file. Make sure that source path and `WatchPaths` path match. Add two target folders, if you want to put photos and videos into separate folders.

- `media_mgmt_helper.py` location
- Source folder
- Target folder(s)
- StandardOutPath
- StandardErrorPath

Move your custom LaunchAgent plist to user `LaunchAgents` folder:

`$ mv path/to/com.yourdomain.media_mgmt_helper.plist ~/Library/LaunchAgents/`

Load LaunchAgent:

`$ launchctl load ~/Library/LaunchAgents/com.yourdomain.media_mgmt_helper.plist`

Make sure that `media_mgmt_helper.py` has execute file permissions for LaunchAgent to work properly.
