#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
media_mgmt_helper.py -- util for moving photo and video files (inside Dropbox)

Copyright (c) 2015 Janne Lehikoinen

This script copies photos and videos from one source folder
to one target folder or two separate target folders.

Folder(s) are created based on DateTimeOriginal or CreateDate metadata.

"""

"""
TODO
- 'Mass mover' option?
"""

import os
import sys
import datetime
import subprocess
import logging
import re

"""
EDIT THESE GLOBAL VARIABLES >>>>>
"""

# 1 - File types

# File types that will be moved to target folder(s)
PICS_EXTENSIONS = ['.jpg', '.JPG']
VIDS_EXTENSIONS = ['.mov', '.MOV']

# 2 - Use ExifTool

# Change to True if ExifTool is used
# Defaults to Swift binary (False)
USE_EXIFTOOL=False

# 3 - Photo and video subfolder descriptions

# These descriptions are added to subfolder names
# if photos and videos go to separate folders.
# Defaults to Finnish
# English example: PICS_DESC = '-photos' & VIDS_DESC = '-videos'
PICS_DESC = '-kuvat'
VIDS_DESC = '-videot'

# 4 - Dropbox folder location

# Defaults to '~/Dropbox'
DROPBOX_ROOT = os.path.expanduser("~") + '/Dropbox'

# 5 - Unsorted files location

# Defaults to '~/Dropbox/Unsorted Media Files'
UNSORTED_FOLDER = DROPBOX_ROOT + '/Unsorted Media Files'

# Optional customization >>>>>

# Binary paths
EXIFTOOL = '/usr/bin/exiftool'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SWIFT_TOOL = SCRIPT_PATH + '/get-metadata'

# Year & month regex
REGEX_YEAR = r'^20\d\d$'
REGEX_MONTH = r'^(0?[1-9]|1[012])$'

# Date&time format in log
TIME_FORMAT = '%d.%m.%Y %H.%M.%S'

"""
>>>>> END GLOBAL VARIABLE EDITING
"""

# Helper functions

def msg_info(msg):
    """Print date & time stamp and message"""

    date_pattern = datetime.datetime.now().strftime(TIME_FORMAT)
    print '%s: %s' % (date_pattern, msg)


def msg_error(msg):
    """Print error message"""

    print 'ERROR: %s' % msg


def msg_usage():
    """Print usage message"""

    print """Usage:

    If one common target folder is used for both photos and videos:
    ./media_mgmt_helper.py path/to/source_folder path/to/target_media

    If two separate target folders are used, one for photos and one for videos:
    ./media_mgmt_helper.py path/to/source_folder path/to/target_photos path/to/target_videos
    """


def preflight_checks():
    """Run few preflight checks"""

    if USE_EXIFTOOL:
        # Check that ExifTool is installed
        if not os.path.exists(EXIFTOOL):
            msg_error('ExifTool not found!')
            sys.exit(1)
    else:
        # Check that custom Swift binary is in place
        if not os.path.exists(SWIFT_TOOL):
            msg_error('Swift binary not found!')
            sys.exit(1)

    # Create UNSORTED_FOLDER if it doesn't exist
    if not os.path.exists(UNSORTED_FOLDER):
        msg_info('Creating new folder: ' + UNSORTED_FOLDER)
        os.makedirs(UNSORTED_FOLDER)


def folder_validator(folder):
    """
    Validate folders and add trailing slash if needed
    Return: full path
    """

    if not os.path.exists(folder):
        msg_error('Folder ' + folder + ' not found!')
        sys.exit(1)

    if not os.path.isdir(folder):
        msg_error(folder + ' is not a folder!')
        sys.exit(1)

    # Add trailing slash to folder if not found
    if not folder.endswith(os.path.sep):
        folder += os.path.sep

    return folder


def get_model_exiftool(file_path):
    """
    Get camera model using ExifTool
    Return: model (e.g. iPhone):
    """

    command = [EXIFTOOL,
               '-s', '-s', '-s',
               '-model', file_path]
    model = call_cmd(command)

    return model


def get_year_month_exiftool(file_path):
    """
    Get year and month from CreateDate tag using ExifTool
    If no CreateDate tag, parse year and month from file name
    Carousel naming convention: 2015-02-12 00.05.58.jpg
    Return: year, month (e.g. 2015 and 02)
    """

    file_name = os.path.basename(file_path)
    command = [EXIFTOOL,
               '-s', '-s', '-s',
               '-createDate', file_path]
    date = call_cmd(command)

    if date:
        # Parse year and month
        year = date[:4]
        month = date[5:7]
    else:
        # Try parsing year and month from file name
        year = file_name[:4]
        month = file_name[5:7]

    # Check that year has valid value
    if not re.match(REGEX_YEAR, year):
        year = ''

    # Check that month has valid value
    if not re.match(REGEX_MONTH, month):
        month = ''

    return year, month


def get_model_swift(file_path):
    """
    Get camera model using Swift
    Return: model (e.g. iPhone):
    """
    file_name_dummy, extension = os.path.splitext(file_path)
    model = ""

    if extension in PICS_EXTENSIONS:
        command = [SWIFT_TOOL, 'photo', 'Model', file_path]
        model = call_cmd(command)
    elif extension in VIDS_EXTENSIONS:
        command = [SWIFT_TOOL, 'video', 'common/model', file_path]
        model = call_cmd(command)

    return model

def get_year_month_swift(file_path):

    """
    Get year and month from DateTimeOriginal metadata using Swift
    If no Create Date tag, parse year name from file name
    Carousel naming convention: 2015-02-12 00.05.58.jpg
    Return: year and month (e.g. 2015 and 02)
    """
    file_name_dummy, extension = os.path.splitext(file_path)
    file_name = os.path.basename(file_path)

    if extension in PICS_EXTENSIONS:
        command = [SWIFT_TOOL, 'photo', 'DateTimeOriginal', file_path]
        date = call_cmd(command)
    elif extension in VIDS_EXTENSIONS:
        command = [SWIFT_TOOL, 'video', 'common/creationDate', file_path]
        date = call_cmd(command)

    if date:
        # Parse year and month
        year = date[:4]
        month = date[5:7]
    else:
        # Try parsing year and month from file name
        year = file_name[:4]
        month = file_name[5:7]

    # Check that year has valid value
    if not re.match(REGEX_YEAR, year):
        year = ''

    # Check that month has valid value
    if not re.match(REGEX_MONTH, month):
        month = ''

    return year, month

def call_cmd(command):
    """
    Subprocess function that runs cli commands
    Return: stdout (white space removed)
    """

    task = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = task.communicate()
    task.wait()

    if err:
        msg_error(err)

    # Strip whitespace from cmd output
    return out.strip()


def create_dir_tree(target_path, year, month, media_type):
    """
    Create directory tree if it doesn't exist
    Return: full target path (e.g. path/to/target/2015/2015-02)
    """

    year_path = target_path + year
    month_path = year_path + '/' + year + \
        '-' + month + media_type

    if not os.path.exists(year_path):
        msg_info('Creating new folder: ' + year_path)
        os.makedirs(year_path)
    if not os.path.exists(month_path):
        msg_info('Creating new folder: ' + month_path)
        os.makedirs(month_path)

    return month_path


def move_file(source_path, target_path, file_name, model):
    """
    Move file to target location
    Don't move file if found in target folder
    """

    last_path = os.path.basename(os.path.normpath(target_path))

    # Construct model string for logging
    if model:
        model = model + ' - '

    # Double check for existing target files
    if os.path.isfile(os.path.join(target_path, file_name)):
        msg_info(file_name + ' already exists in ' +
                 last_path + ' folder so it remains in place')
    else:
        try:
            # Actual move operation
            msg_info(model + 'Moving ' +
                     file_name + ' to ' + last_path)
            os.rename(os.path.join(source_path, file_name),
                      os.path.join(target_path, file_name))
        except OSError as e:
            msg_error(e)
        except IOError as e:
            msg_error(e.strerror)


def main():

    # Preflight checks
    preflight_checks()

    # Vars
    full_paths = []
    one_target_folder = False

    # Check cmd line arguments except the script itself
    args = sys.argv[1:]

    if len(args) == 0:
        msg_usage()
        sys.exit(1)

    if len(args) < 2:
        msg_error('Too few arguments!')
        msg_usage()
        sys.exit(1)

    elif len(args) == 2:
        one_target_folder = True

    elif len(args) > 3:
        msg_error('Too many arguments!')
        msg_usage()
        sys.exit(1)

    # Validate folders and add trailing slash
    for arg in args:
        full_paths.append(folder_validator(arg))

    # Main loop
    for file in os.listdir(full_paths[0]):

        full_source_path = full_paths[0] + file

        # Go through all valid file extensions
        ALL_EXTENSIONS = PICS_EXTENSIONS + VIDS_EXTENSIONS
        if any(file.endswith(x) for x in ALL_EXTENSIONS):

            # Get year and month from file metadata
            if USE_EXIFTOOL:
                model = get_model_exiftool(full_source_path)
                year, month = get_year_month_exiftool(full_source_path)
            else:
                model = get_model_swift(full_source_path)
                year, month = get_year_month_swift(full_source_path)

            # Check for non-empty strings
            if year and month:

                # Create folder structure
                # Handle one or two target folders
                if one_target_folder:
                    target_path = create_dir_tree(full_paths[1], year,
                                                  month, media_type='')
                else:
                    # Handle photo vs. video file types
                    if any(file.endswith(x) for x in PICS_EXTENSIONS):
                        target_path = create_dir_tree(full_paths[1],
                                                      year,
                                                      month,
                                                      media_type=PICS_DESC)
                    elif any(file.endswith(x) for x in VIDS_EXTENSIONS):
                        target_path = create_dir_tree(full_paths[2],
                                                      year,
                                                      month,
                                                      media_type=VIDS_DESC)
                # Move files
                move_file(full_paths[0], target_path, file, model)

            else:
                msg_info(file + ' is missing date metadata')
                # Move files to UNSORTED_FOLDER
                move_file(full_paths[0], UNSORTED_FOLDER, file, model)
    # main loop ends

if __name__ == "__main__":
    main()
