#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
LaunchBox Images To RetroArch Thumbnails
  by JDHatten
    
    Copy images from LaunchBox and add them to RetroArch's thumbnails. With options to choose
    which LaunchBox images to prioritize for each of RetroArch's three thumbnail types
    'Front Boxart', 'Title Screen', and 'Gameplay Screen' (AKA Named_Boxarts, Named_Titles,
    Named_Snaps).
    
    Other features:
    - Modify image sizes
    - Use alternating images for multi-disc games
    
    LaunchBox is a popular frontend for emulator applications, which maintains its own crowd-
    sourced database (user submitted info, images, videos, etc) for a massive number of games.
    - https://www.launchbox-app.com/
    
    RetroArch is a popular frontend that also runs Libretro cores, which are basically emulators
    that have been ported to Libretro/RetroArch.
    - https://www.retroarch.com/


How To Use:
    Simply drag & drop one or more game files (ROMs/Disc/etc) or directories onto this script.
    -OR-
    Run this script in the directory where games files are located.


Requirements:
    Pillow is an imaging library that must be installed in order to modify images.
    - pip install Pillow
    - https://pypi.org/project/Pillow/


TODO:
    [X] Create log file.
    [X] Search only known game extensions.
    [X] Modify image sizes, and maybe other modifications?
        [] Image combining?
        [] Rotation?
    [X] Find a way to match up LaunchBox and RetroArch databases/platforms, for faster searches.
    [] Priorities for Region (NA,Japan,etc), Format (.jpg,.png,etc), and Number (01,02,etc).
        [] Random number option?
    [] 

'''

# Installation root paths to both LaunchBox and RetroArch applications.
launchbox_root = r''
retroarch_root = r''

# A list of file extensions used when searching directories for game files.
# If any of your game file extensions are not included below, add them.
game_extensions = [
  # Standard disc image file extensions used in many different platforms.
  '.chd','.cue','.iso','.mds','.nrg','.toc',
  # Standard rom file extensions used in many different platforms.
  '.bin','.rom',
  # Common archive file extensions.
  '.7z','.rar','.zip',
  # Common playlist file extensions (used for multi-disc games).
  '.m3u',
  # Specific game platform file extensions.
  '.nes',                # Nintendo Entertainment System
  '.sfc','.smc',         # Super Nintendo
  '.n64','.v64','.z64',  # Nintendo 64
  '.gcm',                # Nintendo GameCube
  '.wad','.wbfs',        # Nintendo Wii
  '.gb',                 # Nintendo Game Boy
  '.gbc',                # Nintendo Game Boy Color
  '.gba',                # Nintendo Game Boy Advance
  '.nds',                # Nintendo DS
  '.3ds',                # Nintendo 3DS
  '.pce',                # PC Engine / TurboGrafx-16
  '.sms',                # Sega Master System
  '.32x','.md',          # Sega Genesis / 32X
  '.cdi','.gdi',         # Sega Dreamcast
  '.gg',                 # Sega Game Gear
]

# This script will continue to run allowing the dropping of additional files or directories.
# Set this to False and this script will run once, do it's thing, and close
loop_script = True

# Create a log file that will record all the details of each new RetroArch thumbnail created.
# Note: New log file will overwrite old log file. Rename and save log file once open if you
# want to prevent it being overwritten.
create_log_file = True

# Match LaunchBox and RetroArch platforms before searching through playlists, for faster
# searches. Set to False if your games (that are in both LaunchBox and RetroArch) are not
# having their RetroArch thumbnails created.
# Note: If you have a small amount of games, this won't matter much anyways so set to False.
match_platforms_before_search = True

# Only add platforms that clearly have different spellings. Ignore dashes and text in
# (parenthesis), they will be removed where needed. Also add platforms with games that may be
# included in multiple or different platforms/playlists.
matching_platforms = {
  # LaunchBox                   :  RetroArch
  '3DO Interactive Multiplayer' : ['The 3DO Company - 3DO'],
  'Atari Jaguar'                : ['Atari - Jaguar', 'Atari - Jaguar CD'],
  'Atari Jaguar CD'             : ['Atari - Jaguar', 'Atari - Jaguar CD'],
  'Magnavox Odyssey'            : ['Magnavox - Odyssey2'],
  'Magnavox Odyssey 2'          : ['Magnavox - Odyssey2'],
  'MS-DOS'                      : ['DOS'],
  'NEC PC-9801'                 : ['NEC - PC-98'],
  'NEC TurboGrafx-16'           : ['NEC - PC Engine - TurboGrafx 16', 'NEC - PC Engine CD - TurboGrafx-CD', 'NEC - PC Engine SuperGrafx'],
  'NEC TurboGrafx-CD'           : ['NEC - PC Engine - TurboGrafx 16', 'NEC - PC Engine CD - TurboGrafx-CD', 'NEC - PC Engine SuperGrafx'],
  'Nintendo DS'                 : ['Nintendo - Nintendo DS', 'Nintendo - Nintendo DS Decrypted', 'Nintendo - Nintendo DSi', 'Nintendo - Nintendo DSi Decrypted'],
  'Nintendo DSi'                : ['Nintendo - Nintendo DS', 'Nintendo - Nintendo DS Decrypted', 'Nintendo - Nintendo DSi', 'Nintendo - Nintendo DSi Decrypted'],
  'PC Engine SuperGrafx'        : ['NEC - PC Engine - TurboGrafx 16', 'NEC - PC Engine CD - TurboGrafx-CD', 'NEC - PC Engine SuperGrafx'],
  'Sega 32X'                    : ['Sega - 32X', 'Sega - Mega Drive - Genesis', 'Sega - Mega-CD - Sega CD'],
  'Sega CD'                     : ['Sega - 32X', 'Sega - Mega Drive - Genesis', 'Sega - Mega-CD - Sega CD'],
  'Sega Dreamcast VMU'          : ['Sega - Dreamcast'],
  'Sega Genesis'                : ['Sega - 32X', 'Sega - Mega Drive - Genesis', 'Sega - Mega-CD - Sega CD'],
  'Sinclair ZX Spectrum'        : ['Sinclair - ZX 81', 'Sinclair - ZX Spectrum +3', 'Sinclair - ZX Spectrum'],
  'Sinclair ZX-81'              : ['Sinclair - ZX 81', 'Sinclair - ZX Spectrum +3', 'Sinclair - ZX Spectrum'],
  'Sony PlayStation'            : ['Sony - PlayStation'], # Only to avoid being matched with PlayStation 2/3.
  'Sony PSP'                    : ['Sony - PlayStation Portable', 'Sony - PlayStation Portable Vita'],
  'Sony PSP Minis'              : ['Sony - PlayStation Portable', 'Sony - PlayStation Portable Vita'],
  'VTech CreatiVision'          : ['VTech - CreatiVision', 'VTech - V.Smile'],
  'VTech Socrates'              : ['VTech - CreatiVision', 'VTech - V.Smile'],
}

# You shouldn't have to edit this as it's only used to identify multi-disc game files.
# However, if you have some unique file naming conventions for your games and know how to
# use Regular Expressions, go for it.
# Note: The + are just added for readability.
# Example Matches: "(Disc 1 of 3)", "[CD2]", "(Game Disc 1)" etc
re_disc_info_pattern = ( '\s*' + '(\(|\[)' + '(CD|Disc|Disk|DVD|Game|Game\s*Disc)' +
                         '\s*(\d+)\s*\w*\s*(\d*)' + '(\)|\])' )

# Preset Options
DESCRIPTION = 0
FRONT_BOXART_PRIORITY = 1
TITLE_SCREEN_PRIORITY = 2
GAMEPLAY_SCREEN_PRIORITY = 3
ALTERNATE_BOXART_IMAGES = 4
ALTERNATE_TITLE_IMAGES = 5
ALTERNATE_GAMEPLAY_IMAGES = 6
MODIFY_IMAGE_WIDTH = 7
MODIFY_IMAGE_HEIGHT = 8
IMAGE_RESAMPLING_FILTER = 9
KEEP_ASPECT_RATIO = 10
SEARCH_SUB_DIRS = 11
OVERWRITE_IMAGES = 12

# Image Modifiers
NO_CHANGE = 0          # Keep size as is.
CHANGE_TO = 1          # Change to a specific size.
MODIFY_BY_PIXELS = 2   # Add/subtract to/from current size.
MODIFY_BY_PERCENT = 3  # Percent of current size (50% = current size * 0.5).
UPSCALE = 4            # Only increase to specific size (keep as is if current size is larger).
DOWNSCALE = 5          # Only decrease to specific size (keep as is if current size is smaller).

# Resampling Filters
NEAREST = 0   # [Default]
BILINEAR = 1  # 
BICUBIC = 2   # 

## TODO: Extra Image Saving Parameters (PNG Only)
OPTIMIZE = 3      # Possible optimization values are True or False.
COMPRESSION = 5   # Possible compress levels are between 1-9, default 6, and auto-set to 9 if OPTIMIZE is set to True.


# Default LaunchBox image category priorities when selecting thumbnails for RetroArch.
# Find all media types in LaunchBox "Tools / Manage / Platforms / Edit Platform / Folders / Media Type"
# Note: Don't modify these defaults, use the existing presets or make your own presets instead.
DEFAULT_FRONT_BOXARTS =    ['Box - Front',
                            'Box - Front - Reconstructed',
                            'Fanart - Box - Front',
                            'Box - 3D']
DEFAULT_TITLE_SCREENS =    ['Screenshot - Game Title',
                            'Screenshot - Game Select',
                            'Screenshot - High Scores',
                            'Screenshot - Game Over',
                            'Screenshot - Gameplay']
DEFAULT_GAMEPLAY_SCREENS = ['Screenshot - Gameplay',
                            'Screenshot - Game Select',
                            'Screenshot - Game Over',
                            'Screenshot - High Scores',
                            'Screenshot - Game Title']
SKIP = 0 # Skip media and don't use above defaults.

### Select the default preset to use here. ###
selected_preset = 2

preset0 = { #               : Defaults                  # If option omitted, the default option value will be used.
  DESCRIPTION               : '',                       # Description of this preset.
  FRONT_BOXART_PRIORITY     : DEFAULT_FRONT_BOXARTS,    # A list of LaunchBox image categories (in order of priority) to copy when selecting
  TITLE_SCREEN_PRIORITY     : DEFAULT_TITLE_SCREENS,    #   a front boxart, title screen, and gameplay screen thumbnail for RetroArch.
  GAMEPLAY_SCREEN_PRIORITY  : DEFAULT_GAMEPLAY_SCREENS, ## TODO:   Use SKIP to ignore and not copy any images including defaults.
  ALTERNATE_BOXART_IMAGES   : False,                    # Use different alternating images with multi-disc games if there's more than one image found.
  ALTERNATE_TITLE_IMAGES    : False,                    #   Only used if each disc of a game is added to RetroArch (and not a single m3u playlist).
  ALTERNATE_GAMEPLAY_IMAGES : True,                     #   If set to False the same image will be used for each game disc.
  MODIFY_IMAGE_WIDTH        : NO_CHANGE,                # Modify copied LaunchBox images before saving them as RetroArch thumbnails. Example: ('Image Modifier', Number)
  MODIFY_IMAGE_HEIGHT       : NO_CHANGE,                #   Image Modifiers: CHANGE_TO, MODIFY_BY_PIXELS, MODIFY_BY_PERCENT, UPSCALE, DOWNSCALE
  IMAGE_RESAMPLING_FILTER   : NEAREST,                  # Resampling changes the total number of pixels in an image. Filters: NEAREST, BILINEAR, BICUBIC
  KEEP_ASPECT_RATIO         : True,                     # Keep aspect ratio only if one size, width or height, has changed.
  SEARCH_SUB_DIRS           : False,                    # After searching for games in a directory also search sub-directories.
  OVERWRITE_IMAGES          : False,                    # Overwrite RetroArch thumbnail images, else skip the images that already exist.
}                                                       # 

preset1 = {
  DESCRIPTION               : ('Front and back boxart with a gameplay image. '+
                               'And downscale image heights to 1080.'),
  TITLE_SCREEN_PRIORITY     : ['Box - Back',
                               'Box - Back - Reconstructed',
                               'Fanart - Box - Back',
                               'Screenshot - Game Title'],
  MODIFY_IMAGE_HEIGHT       : (DOWNSCALE, 1080),
  IMAGE_RESAMPLING_FILTER   : BICUBIC,
  KEEP_ASPECT_RATIO         : True,
  SEARCH_SUB_DIRS           : True,
  OVERWRITE_IMAGES          : True
}
preset2 = {
  DESCRIPTION               : ('Front (3D) and back boxart with a cart/disc image. '+
                               'And image heights downscaled to 1080.'),
  FRONT_BOXART_PRIORITY     : ['Box - 3D',
                               'Box - Front',
                               'Box - Front - Reconstructed',
                               'Fanart - Box - Front'],
  TITLE_SCREEN_PRIORITY     : ['Box - Back',
                               'Box - Back - Reconstructed',
                               'Fanart - Box - Back',
                               'Screenshot - Game Title'],
  GAMEPLAY_SCREEN_PRIORITY  : ['Cart - Front',
                               'Disc',
                               'Fanart - Cart - Front',
                               'Fanart - Disc',
                               'Screenshot - Gameplay'],
  MODIFY_IMAGE_HEIGHT       : (DOWNSCALE, 1080),
  IMAGE_RESAMPLING_FILTER   : BICUBIC,
  KEEP_ASPECT_RATIO         : True,
  SEARCH_SUB_DIRS           : True,
  OVERWRITE_IMAGES          : True
}
preset3 = {
  DESCRIPTION               : 'Front (3D) boxart only, with height set to 720.',
  FRONT_BOXART_PRIORITY     : ['Box - 3D',
                               'Box - Front',
                               'Box - Front - Reconstructed',
                               'Fanart - Box - Front'],
  TITLE_SCREEN_PRIORITY     : SKIP, ## TODO: Skip media
  GAMEPLAY_SCREEN_PRIORITY  : SKIP,
  MODIFY_IMAGE_HEIGHT       : (CHANGE_TO, 720),
  IMAGE_RESAMPLING_FILTER   : BICUBIC,
  KEEP_ASPECT_RATIO         : True,
  SEARCH_SUB_DIRS           : True,
  OVERWRITE_IMAGES          : True
}

# Add any newly created presets to this preset_options List.
preset_options = [preset0,preset1,preset2,preset3]#,preset4]



####### Don't Edit Below This Line (unless you know what your doing) #######


# Extra log messages and images are saved in this script's root, not in RetroArch.
debug = False

import configparser
from datetime import datetime
import json
from pathlib import Path, PurePath
try:
    from PIL import Image, UnidentifiedImageError
    pillow_installed = True
except ModuleNotFoundError:
    pillow_installed = False
from os import getenv, startfile as OpenFile, walk as Search
import re
from shutil import copy2 as CopyFile
import sys
import xml.etree.ElementTree as XMLParser

# Application Data
APP_DATA = 7777
LAUNCHBOX =           1
PLATFORMS =            10
ALL_MEDIA_TYPES =       101
MEDIA_TYPE =             1011
DIR_PATH =               1012
GAME_PATHS =            102
IMAGE_PATHS =           103
PLATFORMS_DIR_PATH =   11
RETROARCH =           2
PLAYLISTS_DIR_PATH =   22
THUMBNAILS_DIR_PATH =  23

# Game Images
FRONT_BOXART = FRONT_BOXART_PRIORITY
TITLE_SCREEN = TITLE_SCREEN_PRIORITY
GAMEPLAY_SCREEN = GAMEPLAY_SCREEN_PRIORITY

# Logging Data
LOG_DATA = 137
IMAGES_FOUND = 0
CURRENT_GAME_PATH = 1
SAVED_IMAGE_PATHS = 2
GAME_PATHS_IN_LB_RA = 3
IMAGE_EDITS = 4
TIME_DATA = 5
START_TIME = 50
END_TIME = 51
COMPLETION_TIME = 52

MODIFY_IMAGE_SIZE = 0
ERROR = 9
NOT_SAVED = 90
NEW_SAVE = 91
OVERWRITTEN = 92

# Image Dimension Indexes
ORIGINAL_IMAGE_SIZE = 0
NEW_IMAGE_SIZE = 1
WIDTH = 0
HEIGHT = 1

# Image Modifier Indexes
MODIFIER = 0
NUMBER = 1

# Image File Indexes
IMAGE_SOURCE = 0
IMAGE_OUTPUT = 1
SAVE_INFO = 2
EDIT_ERROR = 2

# Multi-Disc Regular Expression
re_disc_info_compiled_pattern = re.compile(re_disc_info_pattern, re.IGNORECASE)

# Regular Expression to find a number
re_number_compiled_pattern = re.compile( '\d*\.?\d*', re.IGNORECASE )

# Regular Expression to find a text inside (parenthesizes).
re_parenthesis_text_compiled_pattern = re.compile( '\s*\(\w*\s*\w*\)', re.IGNORECASE  )

# Characters not allowed in file names.
illegal_characters = list( '\\|:"<>/?' )

ROOT_DIR = Path(__file__).parent


### Change the preset in use, retaining any log data.
###     (preset) A preset that holds the user options on how to copy and edit images.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def changePreset(preset, all_the_data = {}):
    # If Pillow not installed and the preset selected is attempting to modify images...
    if not pillow_installed and (preset.get(MODIFY_IMAGE_WIDTH) or preset.get(MODIFY_IMAGE_HEIGHT)):
        print('\nYou\'re attempting to modify images without first installing "Pillow".')
        print('Pillow is a Python imaging library that must be installed in order to modify images.')
        print('This includes changing image formats to PNG which is required to work in RetroArch.')
        print('Check the "Requirements" section of this script for more information.')
        input('Press "Enter" to continue script without image modification features.')
        print()
    
    app_data = all_the_data.get(APP_DATA, {}).copy()
    log_data = all_the_data.get(LOG_DATA, {}).copy()
    all_the_data = preset
    
    if not log_data:
        all_the_data[APP_DATA] = {}
        all_the_data[APP_DATA][LAUNCHBOX] = {}
        all_the_data[APP_DATA][LAUNCHBOX][IMAGE_PATHS] = {}
        all_the_data[APP_DATA][RETROARCH] = {}
        all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS] = {}
        
        all_the_data[LOG_DATA] = {}
        all_the_data[LOG_DATA][IMAGES_FOUND] = 0
        all_the_data[LOG_DATA][CURRENT_GAME_PATH] = ''
        all_the_data[LOG_DATA][SAVED_IMAGE_PATHS] = {}
        all_the_data[LOG_DATA][GAME_PATHS_IN_LB_RA] = []
        all_the_data[LOG_DATA][IMAGE_EDITS] = {}
        all_the_data[LOG_DATA][COMPLETION_TIME] = 0
    else:
        all_the_data[APP_DATA] = app_data
        all_the_data[LOG_DATA] = log_data
    
    #print(all_the_data)
    
    return all_the_data


### Get file data and existing paths to needed files and directories from LaunchBox and RetroArch.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def getLaunchBoxRetroArchData(all_the_data):
    print('Checking For LaunchBox and RetroArch Installations...')
    
    global launchbox_root
    global retroarch_root
    
    # If app root paths are pointing to a file instead of just the root, fix it here.
    if Path(launchbox_root).is_file():
        launchbox_root = Path(launchbox_root).parent
    if Path(retroarch_root).is_file():
        retroarch_root = Path(retroarch_root).parent
    
    # Check If LaunchBox and RetroArch Apps Exist
    for app_name, app_path in {'LaunchBox' : launchbox_root, 'RetroArch' : retroarch_root}.items():
        
        # If app root paths are left empty, take some guesses on where the apps might be installed.
        if app_path == '':
            posible_app_locations = [
                Path(PurePath().joinpath(getenv('PROGRAMFILES(X86)'), app_name, f'{app_name}.exe')),
                Path(PurePath().joinpath(getenv('PROGRAMFILES'), app_name, f'{app_name}.exe')),
                Path(PurePath().joinpath(getenv('HOMEDRIVE'), '/', app_name, f'{app_name}.exe')),
                Path(PurePath().joinpath('D:/', 'Apps', app_name, f'{app_name}.exe')),
                Path(PurePath().joinpath('D:/', 'Games', 'Emulators', app_name, f'{app_name}.exe')),
            ]
            for app in posible_app_locations:
                if app.exists():
                    app_path = app.parent
                    if app_name == 'LaunchBox':
                        launchbox_root = app.parent
                    elif app_name == 'RetroArch':
                        retroarch_root = app.parent
        
        # Final check if root paths exist and inform user if they don't.
        if app_path == '' or not Path(app_path).exists():
            if app_path == '':
                print(f'\nERROR: The {app_name} App Was Not Found On This Systme.')
            else:
                print(f'\nERROR: The {app_name} App Does Not Exist Here. [ {app_path} ]')
            print(f'       Make sure {app_name} is installed and that the "{app_name.casefold()}_root" variable in this script is correct.')
            return None
    
    # Get LaunchBox Platform Names, Image Type Data and Image Root Directory Path
    launchbox_platforms_xml_path = Path(PurePath().joinpath(launchbox_root, 'Data', 'Platforms.xml'))
    if launchbox_platforms_xml_path.exists():
        print(f'Getting Platform Names, Image Type and Path Data From: {launchbox_platforms_xml_path}')
        all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS] = {}
        
        platforms_root = XMLParser.parse(launchbox_platforms_xml_path).getroot()
        for image_folders in platforms_root.findall('PlatformFolder'):
            platform = image_folders.find('Platform').text
            madia_type = image_folders.find('MediaType').text
            image_dir_path = Path(image_folders.find('FolderPath').text)
            
            if platform not in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS]:
                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform] = {ALL_MEDIA_TYPES : [], GAME_PATHS: {}, IMAGE_PATHS : {}, }
                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][ALL_MEDIA_TYPES] = [{ MEDIA_TYPE : madia_type, DIR_PATH : image_dir_path }]
                all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform] = {}
                all_the_data[LOG_DATA][IMAGE_EDITS][platform] = {}
            else:
                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][ALL_MEDIA_TYPES].append({ MEDIA_TYPE : madia_type, DIR_PATH : image_dir_path })
    else:
        print(f'\nERROR: LaunchBox\'s "Platforms.xml" File Does Not Exist. [ {launchbox_platforms_xml_path} ]')
        print('       Check if your LaunchBox is installed properly and you have games imported into LaunchBox.')
        return None
    
    # Get LaunchBox Platforms Directory Path
    launchbox_platforms_dir_path = Path(PurePath().joinpath(launchbox_root, 'Data', 'Platforms'))
    if launchbox_platforms_dir_path.exists():
        print(f'Found LaunchBox Platforms Directory: {launchbox_platforms_dir_path}')
        all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS_DIR_PATH] = launchbox_platforms_dir_path
    else:
        print(f'\nERROR: LaunchBox\'s "Platforms" Directory Does Not Exist. [ {launchbox_platforms_dir_path} ]')
        print('       Check if your LaunchBox is installed properly and you have games imported into LaunchBox.')
        return None
    
    # Get RetroArch Playlists and Thumbnails Directory Paths
    retroarch_config_path = Path(PurePath().joinpath(retroarch_root, 'retroarch.cfg'))
    if retroarch_config_path.exists():
        with open(retroarch_config_path, 'r') as file:
            retroarch_config_string = '[SETTINGS]\n' + file.read()
        retroarch_config_file = configparser.ConfigParser()
        #retroarch_config_file.read(retroarch_config_path)
        retroarch_config_file.read_string(retroarch_config_string)
        
        retroarch_playlists = retroarch_config_file['SETTINGS'].get('playlist_directory')
        if retroarch_playlists:
            retroarch_playlists_path = getPathFromSetting(retroarch_playlists, retroarch_root)
        else:
            retroarch_playlists_path = None
        
        if retroarch_playlists_path and retroarch_playlists_path.exists():
            print(f'Found RetroArch Playlists Directory: {retroarch_playlists_path}')
            all_the_data[APP_DATA][RETROARCH][PLAYLISTS_DIR_PATH] = retroarch_playlists_path
        else:
            print(f'\nERROR: RetroArch\'s "Playlist" Directory Does Not Exist. [ {retroarch_playlists_path} ]')
            print('       Update your RetroArch\'s "Settings / Directory / Playlists" settings.')
            return None
        
        retroarch_thumbnails = retroarch_config_file['SETTINGS'].get('thumbnails_directory')
        if retroarch_thumbnails:
            retroarch_thumbnails_path = getPathFromSetting(retroarch_thumbnails, retroarch_root)
        else:
            retroarch_thumbnails_path = None
        
        if retroarch_thumbnails_path and retroarch_thumbnails_path.exists():
            print(f'Found RetroArch Thumbnails Directory: {retroarch_thumbnails_path}')
            all_the_data[APP_DATA][RETROARCH][THUMBNAILS_DIR_PATH] = retroarch_thumbnails_path
        else:
            print(f'\nERROR: RetroArch\'s "Thumbnails" Directory Does Not Exist. [ {retroarch_thumbnails_path} ]')
            print('       Update your RetroArch\'s "Settings / Directory / Thumbnails".')
            return None
    
    return all_the_data


### Get directory path from a RetroArch setting.
###     (setting) A string from a settings file.
###     (root) Root path if setting is a relative path.
###     --> Returns a [Path]
def getPathFromSetting(setting, root = None):
    if setting[:2] == '":':
        setting_path = Path(setting[2:-1].strip('/\\')) # Remove Colon and Quotes and trim slashes
        if root:
            setting_path = Path(PurePath().joinpath(root, setting_path))
    else:
        setting_path = Path(setting[1:-1]).resolve() # Remove Quotes
    
    return setting_path


### Find game paths in LaunchBox various platform files and record needed image file paths.
###     (path) A Path or List of Paths to a game file or a directory of games.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def findLaunchBoxGameImages(path, all_the_data):
    search_sub_dirs = all_the_data.get(SEARCH_SUB_DIRS, False)
    paths = makeList(path)
    
    all_the_data[LOG_DATA][START_TIME] = datetime.now().timestamp()
    
    for path in paths:
        
        if not Path(path).exists():
            print(f'Does Not Exist: {path}')
            continue
        
        if Path(path).is_file():
            
            game_path = Path(path)
            all_the_data[LOG_DATA][CURRENT_GAME_PATH] = game_path
            all_the_data = searchForGameImages(all_the_data)
        
        elif Path(path).is_dir():
            
            for root, dirs, files in Search(path):
                for file in files:
                    
                    game_path = Path(PurePath().joinpath(root, file))
                    all_the_data[LOG_DATA][CURRENT_GAME_PATH] = game_path
                    
                    # Only known game file extensions
                    if game_path.suffix in game_extensions:
                        all_the_data = searchForGameImages(all_the_data)
                
                if not search_sub_dirs:
                    break
    
    all_the_data[LOG_DATA][END_TIME] = datetime.now().timestamp()
    all_the_data[LOG_DATA][COMPLETION_TIME] += all_the_data[LOG_DATA][END_TIME] - all_the_data[LOG_DATA][START_TIME]
    
    return all_the_data


### Search for the correct game images and record thier paths.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def searchForGameImages(all_the_data):
    game_path = all_the_data[LOG_DATA][CURRENT_GAME_PATH]
    
    # Detect multi-disc games
    is_multidisc_game = re_disc_info_compiled_pattern.search(game_path.stem)
    
    print(f'\nSearching For LaunchBox Images Of The Game: {game_path.name}')
    game_found = False
    
    for root, dirs, files in Search(all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS_DIR_PATH]):
        
        for file in files:
            if Path(file).suffix == '.xml':
                xml_file_path = Path(PurePath().joinpath(root, file))
                xml_file_data = XMLParser.parse(xml_file_path).getroot()
                
                # Find games in <Game> (default) and <AdditionalApplication> (additional discs, regions, versions, hacks, etc)
                ## TODO: variants in AdditionalApplication other than multi-disc games
                app_id = 'zzzzzzzzzz'
                game_id = 'xxxxxxxxxx'
                
                if is_multidisc_game:
                    for game_data in xml_file_data.findall('AdditionalApplication'):
                        app_path = game_data.find('ApplicationPath').text
                        if app_path == str(game_path):
                            app_id = game_data.find('GameID').text
                            break
                
                for game_data in xml_file_data.findall('Game'):
                    app_path = game_data.find('ApplicationPath').text
                    
                    if is_multidisc_game:
                        game_id = game_data.find('ID').text
                    
                    if app_path == str(game_path) or game_id == app_id:
                        platform = game_data.find('Platform').text
                        game_title = game_data.find('Title').text
                        
                        if debug: print(f'  <ApplicationPath>{app_path}</ApplicationPath>')
                        if debug: print(f'  <Platform>{platform}</Platform>')
                        if debug: print(f'  <Title>{game_title}</Title>')
                        
                        if platform in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS]:
                            print(f'\nSearching for best image to use for a RetroArch Boxart thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, platform, game_title, FRONT_BOXART, DEFAULT_FRONT_BOXARTS)
                            print(f'\nSearching for best image to use for a RetroArch Title thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, platform, game_title, TITLE_SCREEN, DEFAULT_TITLE_SCREENS)
                            print(f'\nSearching for best image to use for a RetroArch Snap thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, platform, game_title, GAMEPLAY_SCREEN, DEFAULT_GAMEPLAY_SCREENS)
                            
                            #print(all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][IMAGE_PATHS][game_title])
                            
                            if game_title in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform].get(GAME_PATHS, {}):
                                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][GAME_PATHS][game_title].append(game_path)
                            else:
                                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][GAME_PATHS].update({game_title : [game_path]})
                        
                        game_found = True
                        break
                
                if game_found: break
        if game_found: break
    
    return all_the_data


### Record and properly categorize images to later transfer to RetroArch.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     (platform) Game platform string.
###     (game_title) Game title string.
###     (media) Key name of image category priority option.
###     (default_media) Default list of image categories.
###     --> Returns a [Dictionary]
def saveImagePaths(all_the_data, platform, game_title, media, default_media = {}):
    platform_data = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].get(platform)
    media_type_list = all_the_data.get(media, default_media)
    
    if not platform_data[IMAGE_PATHS].get(game_title):
        platform_data[IMAGE_PATHS][game_title] = {}
    
    # Get alternate images to use with multi-disc games
    existing_images = makeList(platform_data[IMAGE_PATHS][game_title].get(media, []))
    
    for media_type in media_type_list:
        for path_data in platform_data[ALL_MEDIA_TYPES]:
            #print(path_data[MEDIA_TYPE])
            
            if media_type == path_data[MEDIA_TYPE]:
                ## TODO: Image number pref? (01,02,...) also (search) Format/Extension pref? PNG or JPG
                ## TODO: NEW in LaunchBox. "Game Title.<ID>-01"  Have to search with and without ID (from xml) to find images ??
                ## TODO: Region prefs?
                #file_name = f'{game_title.replace(":","_")}-01'
                
                partial_file_name = f'{game_title}'
                for ic in illegal_characters:
                    partial_file_name = partial_file_name.replace(ic,'_')
                
                image_file_path = searchImageDirectory(path_data[DIR_PATH], partial_file_name, existing_images)
                
                if image_file_path:
                    print(f'Found: {image_file_path}')
                    all_the_data[LOG_DATA][IMAGES_FOUND] += 1
                    
                    if existing_images:
                        existing_images.append(image_file_path)
                    
                    platform_data[IMAGE_PATHS][game_title].update(
                        { media : existing_images if existing_images else [image_file_path] }
                    )
                    
                    return all_the_data
    
    return all_the_data


### Search for an image file name within the directory provided and return the full Path.
###     (directory) A full Path to a directory.
###     (partial_file_name) Part of a file name string minus the extension.
###     (ignore_files_list) List of files to ignore (because already found).
###     --> Returns a [Path]
def searchImageDirectory(directory, partial_file_name, ignore_files_list = []):
    file_found = None
    for root, dirs, files in Search(directory):
        for file in files:
            file_path = Path(PurePath().joinpath(root, file))
            if file_path in ignore_files_list: continue
            
            # Match: [Game Title] + [.<ID>-##] or [-##]
            if re.match(f'{partial_file_name}[\.|\-]' , file_path.stem, re.IGNORECASE):
                return file_path
    
    return file_found


### Create RetroArch thumbnail file paths for each LaunchBox image found.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def createRetroArchImagePaths(all_the_data):
    retroarch_thumbnails_root = all_the_data[APP_DATA][RETROARCH][THUMBNAILS_DIR_PATH]
    if debug: debug_thumbnails_root = Path(PurePath().joinpath(ROOT_DIR,'thumbnails'))
    
    all_the_data[LOG_DATA][START_TIME] = datetime.now().timestamp()
    
    for platform, data in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].items():
        for game_title, media in data[IMAGE_PATHS].items():
            
            launchbox_front_boxart_paths = media.get(FRONT_BOXART, [None])
            launchbox_title_screen_paths = media.get(TITLE_SCREEN, [None])
            launchbox_gameplay_screen_paths = media.get(GAMEPLAY_SCREEN, [None])
            
            print('\nGame Title:')
            print(f'  {game_title}')
            print('Usable Front Boxart Images:')
            boxart_paths = ",\n  ".join([str(path) for path in launchbox_front_boxart_paths])
            print(f'  {boxart_paths}')
            print('Usable Title Screen Images:')
            title_paths = ",\n  ".join([str(path) for path in launchbox_title_screen_paths])
            print(f'  {title_paths}')
            print('Usable Gameplay Screen Images:')
            gameplay_paths = ",\n  ".join([str(path) for path in launchbox_gameplay_screen_paths])
            print(f'  {gameplay_paths}')
            
            game_paths = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][GAME_PATHS][game_title]
            #print(f'Game Paths: {game_paths}')
            
            for root, dirs, files in Search(all_the_data[APP_DATA][RETROARCH][PLAYLISTS_DIR_PATH]):
                for file in files:
                    if Path(file).suffix == '.lpl':
                        
                        retroarch_playlist_path = Path(PurePath().joinpath(root, file))
                        launchbox_platform_name = platform
                        retroarch_platform_name = retroarch_playlist_path.stem
                        
                        # Only search playlist files if they belong to the same platform.
                        if match_platforms_before_search:
                            # Remove any ' (text)' from RetroArch platforms/playlists.
                            para_text = re_parenthesis_text_compiled_pattern.findall(retroarch_platform_name)
                            retroarch_platform_name_match = retroarch_platform_name
                            for remove_text in para_text:
                                retroarch_platform_name_match = retroarch_platform_name_match.replace(remove_text, '')
                            
                            # Only search though playlist if platforms are the same (skip others to save time).
                            if launchbox_platform_name in matching_platforms:
                                if retroarch_platform_name_match not in matching_platforms[launchbox_platform_name]:
                                    continue
                            else:
                                if retroarch_platform_name.find('Nintendo - ') > -1:
                                    retroarch_platform_name_match = retroarch_platform_name.replace('Nintendo - ','').casefold()
                                if retroarch_platform_name.find('Bandai - ') > -1:
                                    retroarch_platform_name_match = retroarch_platform_name.replace('Bandai - ','').casefold()
                                if retroarch_platform_name.find('Coleco - ') > -1:
                                    retroarch_platform_name_match = retroarch_platform_name.replace('Coleco - ','').casefold()
                                
                                retroarch_platform_name_match = retroarch_platform_name.replace(' - ',' ').casefold()
                                if retroarch_platform_name_match.find(launchbox_platform_name.casefold()) == -1:
                                    continue
                        
                        if debug: print(f'Game in LB Platform: {launchbox_platform_name}, Searching RA Platform: {retroarch_platform_name}')
                        
                        # Open and Read RetroArch Playlist File
                        retroarch_playlist_file = open(retroarch_playlist_path, 'r', encoding="UTF-8") # "cp866")
                        retroarch_game_data = json.load(retroarch_playlist_file)['items']
                        
                        for game in retroarch_game_data:
                            
                            for game_path in game_paths:
                                
                                if game['path'] == str(game_path):
                                    #print('Game Title:')
                                    #print(f'  {game["label"]}')
                                    print('Game Path (Found In Both LaunchBox and RetroArch):')
                                    print(f'  {game["path"]}')
                                    print('New RetroArch Thumbnail Paths:')
                                    #print(f'Database Name: {game["db_name"]}')
                                    #retroarch_platform_name = Path(game["db_name"]).stem
                                    
                                    if not all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS].get(game_path):
                                        all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path] = {}
                                        all_the_data[LOG_DATA][GAME_PATHS_IN_LB_RA].append(game_path)
                                    
                                    # Create new RetroArch image paths
                                    # Note: Image files are saved in this script's root when debuging.
                                    if launchbox_front_boxart_paths[0]:
                                        retroarch_front_boxart_path = Path(PurePath().joinpath(
                                            debug_thumbnails_root if debug else retroarch_thumbnails_root,
                                            retroarch_platform_name,
                                            'Named_Boxarts',
                                            f'{game["label"]}.png'
                                        ))
                                        print(f'  {retroarch_front_boxart_path}')
                                        all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path].update({
                                            FRONT_BOXART : retroarch_front_boxart_path
                                        })
                                        createRetroArchThumbnailImages(
                                            all_the_data,
                                            launchbox_front_boxart_paths,
                                            retroarch_front_boxart_path,
                                            platform, game_title, game_path, FRONT_BOXART
                                        )
                                    if launchbox_title_screen_paths[0]:
                                        retroarch_title_screen_path = Path(PurePath().joinpath(
                                            debug_thumbnails_root if debug else retroarch_thumbnails_root,
                                            retroarch_platform_name,
                                            'Named_Titles',
                                            f'{game["label"]}.png'
                                        ))
                                        print(f'  {retroarch_title_screen_path}')
                                        all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path].update({
                                            TITLE_SCREEN : retroarch_title_screen_path
                                        })
                                        createRetroArchThumbnailImages(
                                            all_the_data,
                                            launchbox_title_screen_paths,
                                            retroarch_title_screen_path,
                                            platform, game_title, game_path, TITLE_SCREEN
                                        )
                                    if launchbox_gameplay_screen_paths[0]:
                                        retroarch_gameplay_screen_path = Path(PurePath().joinpath(
                                            debug_thumbnails_root if debug else retroarch_thumbnails_root,
                                            retroarch_platform_name,
                                            'Named_Snaps',
                                            f'{game["label"]}.png'
                                        ))
                                        print(f'  {retroarch_gameplay_screen_path}')
                                        all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path].update({
                                            GAMEPLAY_SCREEN : retroarch_gameplay_screen_path
                                        })
                                        createRetroArchThumbnailImages(
                                            all_the_data,
                                            launchbox_gameplay_screen_paths,
                                            retroarch_gameplay_screen_path,
                                            platform, game_title, game_path, GAMEPLAY_SCREEN
                                        )
                        
                        # Close RetroArch Playlist File
                        retroarch_playlist_file.close()
                
                break # Ignore Sub-Directories
    
    all_the_data[LOG_DATA][END_TIME] = datetime.now().timestamp()
    all_the_data[LOG_DATA][COMPLETION_TIME] += all_the_data[LOG_DATA][END_TIME] - all_the_data[LOG_DATA][START_TIME]
    
    return all_the_data


### TODO
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def createRetroArchThumbnailImages(all_the_data, image_source_paths, image_output_path, platform, game_title, game_path, media):
    width_change = all_the_data.get(MODIFY_IMAGE_WIDTH, NO_CHANGE)
    height_change = all_the_data.get(MODIFY_IMAGE_HEIGHT, NO_CHANGE)
    resampling_filter = all_the_data.get(IMAGE_RESAMPLING_FILTER, NEAREST)
    keep_aspect_ratio = all_the_data.get(KEEP_ASPECT_RATIO, True)
    overwrite_retroarch_thumbnails = all_the_data.get(OVERWRITE_IMAGES, False)
    
    ## TODO: do thumbnail creation all at once, on command?
    '''for platform, data in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].items():
        for game_title, image_path_data in data[IMAGE_PATHS].items():
            print(f'\nFront Boxart: {image_path_data[FRONT_BOXART]}')
            print(f'Title Screen: {image_path_data[TITLE_SCREEN]}')
            print(f'Gameplay Screen: {image_path_data[GAMEPLAY_SCREEN]}')
            game_paths = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][platform][GAME_PATHS][game_title]
            
            for game_path in game_paths:
                # Check if game is also in RetroArch (true if image paths were created)
                if all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS].get(game_path):
                    
                    for media, image_source_paths in image_path_data.items():
                        image_output_path = all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path][media]
    '''
    
    current_game_image_paths_log = all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform].get(game_title)
    if not current_game_image_paths_log:
        all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform][game_title] = { game_path : {} }
    elif not all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform][game_title].get(game_path):
        all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform][game_title][game_path] = {}
    current_game_image_paths_log = all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][platform][game_title]
    
    # Get next image from source list
    next_alt_image = 0
    if len(image_source_paths) > 1 and current_game_image_paths_log:
        if media == FRONT_BOXART:
            use_image_alt = all_the_data.get(ALTERNATE_BOXART_IMAGES, False)
        elif media == TITLE_SCREEN:
            use_image_alt = all_the_data.get(ALTERNATE_TITLE_IMAGES, False)
        elif media == GAMEPLAY_SCREEN:
            use_image_alt = all_the_data.get(ALTERNATE_GAMEPLAY_IMAGES, True)
        else:
            use_image_alt = False
        if use_image_alt:# and current_game_image_paths_log.get(game_path):
            for game_path, media_types in current_game_image_paths_log.items():
                for media_type, save_data in media_types.items():
                    if media_type == media:
                         if type(save_data[SAVE_INFO]) == int and save_data[SAVE_INFO] > 0:
                            next_alt_image += 1
                            # Start over and repeat if max hit
                            while next_alt_image >= len(image_source_paths):
                                next_alt_image -= len(image_source_paths)
    
    image_source_path = image_source_paths[next_alt_image]
    
    if pillow_installed and image_output_path.exists() and overwrite_retroarch_thumbnails:
        image_source = Image.open(image_source_path)
    elif pillow_installed and not image_output_path.exists():
        image_source = Image.open(image_source_path)
    else:
        image_source = None
    
    # Image Modification
    if pillow_installed and image_source and (width_change or height_change):
        if not all_the_data[LOG_DATA][IMAGE_EDITS][platform].get(game_title):
            all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title] = {}
        if not all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title].get(game_path):
            all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path] = {
                FRONT_BOXART : {}, TITLE_SCREEN : {}, GAMEPLAY_SCREEN : {}
            }
        if not all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media].get(image_output_path):
            all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media][image_output_path] = {}
        
        current_game_image_edit_log = all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media][image_output_path]
        current_game_image_edit_log[MODIFY_IMAGE_SIZE] = [ (image_source.width, image_source.height) ]
        
        try:
            if debug: print(f'  Org Image Size: {image_source.width} x {image_source.height}')
            image_source = resizeImage(
                image_source,
                width_change,
                height_change,
                keep_aspect_ratio,
                resampling_filter
            )
            if debug: print(f'  New Image Size: {image_source.width} x {image_source.height}')
            
            # Add new image size to log only if it has changed.
            if (image_source.width, image_source.height) not in current_game_image_edit_log[MODIFY_IMAGE_SIZE]:
                current_game_image_edit_log[MODIFY_IMAGE_SIZE].append(
                    (image_source.width, image_source.height)
                )
        
        except (FileNotFoundError, TypeError, UnidentifiedImageError, ValueError) as err:
            error = f'Image Resize Failed: {err}'
            print(error)
            current_game_image_edit_log[ERROR] = error
    
    # Image Save
    if image_output_path.exists():
        if overwrite_retroarch_thumbnails:
            file_saved = OVERWRITTEN
            image_output_path.unlink(missing_ok=True) # Delete
            ## TODO: rename and delete later after successful save. if save error, revert rename.
        else:
            file_saved = NOT_SAVED
    else:
        file_saved = NEW_SAVE
    
    if image_source:
        try:
            createMissingDirectories(image_output_path)
            image_source.save(image_output_path)
            error = None
        except (OSError, ValueError) as err:
            error = f'Failed To Save Image: {err}'
            print(error)
            file_saved = error
    
    # Alt: Copy and paste image file if Pillow not installed.
    elif not pillow_installed and file_saved != NOT_SAVED:
        if image_source_path.suffix == '.png':
            createMissingDirectories(image_output_path)
            CopyFile(image_source_path, image_output_path)
        else:
            print('  -WARNING: Without "Pillow" installed non-PNG images will not work in RetroArch.')
            print(f'  -Skipping image file: {image_source_path}')
            ## TODO: Only PNG when gathering LaunchBox images if no Pillow
    
    current_game_image_paths_log[game_path][media] = [
        image_source_path, image_output_path, file_saved
    ]
    
    return all_the_data


### Resize an image.
###     (image) An Image that is to be resized.
###     (width_change) A Tuple with specific data on how to modify the width of an image.
###     (height_change) A Tuple with specific data on how to modify the height of an image.
###     (keep_aspect_ratio) Keep aspect ratio only if one size, width or height, has changed.
###     (resample) Resampling filter to use while modifying an Image.
###     --> Returns a [Image]
def resizeImage(image, width_change, height_change, keep_aspect_ratio = True, resample = NEAREST):
    if resample == BILINEAR:  resample = Image.Resampling.BILINEAR
    elif resample == BICUBIC: resample = Image.Resampling.BICUBIC
    else:                     resample = Image.Resampling.NEAREST
    
    if width_change or height_change:
        new_width, new_height = modifyImageSize((image.width, image.height), (width_change, height_change), keep_aspect_ratio)
        image = image.resize((new_width, new_height), resample=resample, box=None, reducing_gap=None)
    
    return image


### Modify the size/shape of an image.
###     (org_image_shape) The height and width of the orginal image. ( Width, Height )
###     (image_size_modifications) How to modify the height and width of the orginal image. [ ( Modifier, Width ), ( Modifier, Height ) ]
###     (keep_aspect_ratio) True or False
###     --> Returns a [Tuple] (Height, Width)
def modifyImageSize(org_image_shape, image_size_modifications, keep_aspect_ratio = True):
    # Width
    if type(image_size_modifications[WIDTH]) is tuple:
        
        if image_size_modifications[WIDTH][MODIFIER] == NO_CHANGE:
            new_width = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == CHANGE_TO:
            new_width = image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[WIDTH][NUMBER]) == str:
                percent_number = re_number_compiled_pattern.search(image_size_modifications[WIDTH][NUMBER])
                if percent_number:
                    multipler = float(percent_number).group().strip() / 100
                    new_width = org_image_shape[WIDTH] * multipler
                else:
                    print(f'Error: Can\'t decipher what kind of number this is: {image_size_modifications[WIDTH]}')
                    new_width = org_image_shape[WIDTH]
            else:
                multipler = image_size_modifications[WIDTH][NUMBER] / 100
                new_width = org_image_shape[WIDTH] * multipler
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PIXELS:
            new_width = org_image_shape[WIDTH] + image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == UPSCALE:
            if org_image_shape[WIDTH] < image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == DOWNSCALE:
            if org_image_shape[WIDTH] > image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
    
    elif image_size_modifications[WIDTH] != NO_CHANGE:
        new_width = image_size_modifications[WIDTH]
    
    else:
        new_width = org_image_shape[WIDTH]
    
    # Height
    if type(image_size_modifications[HEIGHT]) is tuple:
        
        if image_size_modifications[HEIGHT][MODIFIER] == NO_CHANGE:
            new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == CHANGE_TO:
            new_height = image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[HEIGHT][NUMBER]) == str:
                percent_number = re_number_compiled_pattern.search(image_size_modifications[HEIGHT][NUMBER])
                if percent_number:
                    multipler = float(percent_number.group().strip()) / 100
                    new_height = org_image_shape[HEIGHT] * multipler
                else:
                    print(f'Error: Can\'t decipher what kind of number this is: {image_size_modifications[HEIGHT]}')
                    new_height = org_image_shape[HEIGHT]
            else:
                multipler = image_size_modifications[HEIGHT][NUMBER] / 100
                new_height = org_image_shape[HEIGHT] * multipler
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PIXELS:
            new_height = org_image_shape[HEIGHT] + image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == UPSCALE:
            if org_image_shape[HEIGHT] < image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == DOWNSCALE:
            if org_image_shape[HEIGHT] > image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
    
    elif image_size_modifications[HEIGHT] != NO_CHANGE:
        new_height = image_size_modifications[HEIGHT]
    
    else:
        new_height = org_image_shape[HEIGHT]
    
    # Aspect Ratio
    if keep_aspect_ratio and image_size_modifications[WIDTH] == NO_CHANGE and image_size_modifications[HEIGHT] != NO_CHANGE :
        factor_w = org_image_shape[WIDTH] / org_image_shape[HEIGHT]
        new_width = org_image_shape[WIDTH] - (org_image_shape[HEIGHT] - new_height) * factor_w
    
    elif keep_aspect_ratio and image_size_modifications[HEIGHT] == NO_CHANGE and image_size_modifications[WIDTH] != NO_CHANGE:
        factor_h = org_image_shape[HEIGHT] / org_image_shape[WIDTH]
        new_height = org_image_shape[HEIGHT] - (org_image_shape[WIDTH] - new_width) * factor_h
    
    new_width = round(new_width)
    new_height = round(new_height)
    #print(f'Width: [{new_width}]  X  Height: [{new_height}]')
    
    return new_width, new_height


### Create any missing directories in a path if they don't already exists.
###     (path) A full absolute path.
###     --> Returns a [Boolean]
def createMissingDirectories(path):
    path = Path(path)
    if path.is_absolute():
        for i in reversed(range(0, len(path.parents))):
            path.parents[i].mkdir(mode=0o777, parents=False, exist_ok=True)
    return Path(path).exists()


### Make any variable a list if not already a list tuple for looping purposes.
###     (variable) A variable of any kind.
###     --> Returns a [List] or [Tuple]
def makeList(variable):
    if variable == None:
        variable = []
    elif type(variable) != list and type(variable) != tuple:
        variable = [variable]
    return variable


### Create log file for all LaunchBox images found and RetroArch thumbnails created.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     (log_file_path) Path of a log file.
###     --> Returns a [Boolean]
def createLogFile(all_the_data, log_file_path = None):
    log_file_created = False
    log_data = all_the_data.get(LOG_DATA)
    save_msg = { NOT_SAVED   : 'Image File Not Saved (A File With The Same Name Already Exists)',
                 NEW_SAVE    : 'New Image File Created',
                 OVERWRITTEN : 'Image File Overwritten' }
    base_arrow = '----> '
    
    if log_data:
        (formated_completion_time, launchbox_images_found, games_found_in_lb_ra,
         image_edit_errors, image_files_saved, image_save_errors) = getLogNumbers(all_the_data)
    else:
        print('\nNo log data found.')
        return False
    
    # Print general details of images found and created
    text_lines = []
    text_lines.append('=================================')
    text_lines.append('= LaunchBox Images              =')
    text_lines.append('=  To RetroArch Thumbnails      =')
    text_lines.append('=================================')
    text_lines.append(f'- Game Files Found in Both LaunchBox and RetroArch: {games_found_in_lb_ra}')
    text_lines.append(f'- Total Usable LaunchBox Images Found: {launchbox_images_found}')
    text_lines.append(f'- Amount of RetroArch Thumbnails Saved: [ {image_files_saved} ]')
    if image_save_errors:
        text_lines.append(f'- Images Not Saved Due To Errors: {image_save_errors}')
    if image_edit_errors:
        text_lines.append(f'- Images That Failed Editing*: [ {image_edit_errors} ]')
        text_lines.append('*If an error happens while editing an image, it still keeps it\'s previous edits and can still be saved.')
    
    text_lines.append(f'\n- Time To Completion: [ {formated_completion_time} ]')
    
    print_text_lines = text_lines.copy()
    print('\n'+'\n'.join(print_text_lines))
    
    # Only create a log file when images are saved or errors happened.
    if image_files_saved + image_save_errors == 0:
        return False
    
    if create_log_file:
        
        if not log_file_path:
            log_file_name = f'{Path(__file__).stem}__log.txt'
            log_file_path = Path(PurePath().joinpath(ROOT_DIR, log_file_name))
        
        desc = all_the_data.get(DESCRIPTION)
        if desc and desc != '':
            text_lines.append('\nPreset Used Description:')
            text_lines.append(f'  {desc}')
        
        for platform, game_titles in log_data[SAVED_IMAGE_PATHS].items():
            for game_title, game_paths in game_titles.items():
                text_lines.append(f'\nGame Title: 	   {game_title}')
                
                for game_path, media_types in game_paths.items():
                    text_lines.append(f'  Game File:  	   {game_path}')
                    
                    for media, image_save_data in media_types.items():
                        image_source = image_save_data[IMAGE_SOURCE]
                        image_output = image_save_data[IMAGE_OUTPUT]
                        save_info = image_save_data[SAVE_INFO]
                        
                        text_lines.append(f'  From LaunchBox:  {image_source}')
                        if type(save_info) != int:
                            text_lines.append(f'    To RetroArch:  ERROR - {save_info}')
                        else:
                            text_lines.append(f'    To RetroArch:  {image_output}')
                            
                            image_edit_error = all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media][image_output].get(ERROR)
                            image_size_edits = all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media][image_output].get(MODIFY_IMAGE_SIZE)
                            if image_edit_error:
                                text_lines.append(f'           {base_arrow}    {image_edit_error}')
                            elif image_size_edits and len(image_size_edits) > NEW_IMAGE_SIZE:
                                org_w = image_size_edits[ORIGINAL_IMAGE_SIZE][WIDTH]
                                org_h = image_size_edits[ORIGINAL_IMAGE_SIZE][HEIGHT]
                                new_w = image_size_edits[NEW_IMAGE_SIZE][WIDTH]
                                new_h = image_size_edits[NEW_IMAGE_SIZE][HEIGHT]
                                text_lines.append(f'           {base_arrow}    Image Size Changed From: [ {org_w} x {org_h} -To- {new_w} x {new_h} ]')
                            #text_lines.append(f'           {base_arrow}    Image Rotated: [ {} ]')
                            text_lines.append(f'           {base_arrow}    Save Details: [ {save_msg[save_info]} ]')
        
        try: # Write Log File
            log_file_path.write_text('\n'.join(text_lines), encoding='utf-8', errors='strict')
            log_file_created = log_file_path # return log file path
        except (OSError, UnicodeError, ValueError) as error:
            print(f'\nCouldn\'t save log file due to a {type(error).__name__}: {type(error).__doc__}')
            print(f'{error}\n')
    
    else:
        print('Log file creation turned off.')
    
    return log_file_created


### Get the log numbers on the total amount of images found, edited, and saved as well as any errors.
###     (all_the_data) A Dictionary of all the details on what images to find and how to
###                    handle them with logs of everything done so far.
###     --> Returns a [String] and [Integer] x 5
def getLogNumbers(all_the_data):
    completion_time = all_the_data[LOG_DATA].get(COMPLETION_TIME, 0)
    launchbox_images_found = all_the_data[LOG_DATA][IMAGES_FOUND]
    games_found_in_lb_ra = len(all_the_data[LOG_DATA][GAME_PATHS_IN_LB_RA])
    image_edit_errors = 0
    image_files_saved = 0
    image_save_errors = 0
    
    # Time Formating
    completion_time = round(completion_time, 1)
    if completion_time >= 3600:
        time_format = '%H:%M:%S.%f'
    elif completion_time >= 60:
        time_format = '%M:%S.%f'
    else:
        time_format = '%S.%f'
    if debug: print(completion_time)
    formated_completion_time = datetime.fromtimestamp(completion_time).strftime(time_format)[:-5].rstrip('.0')
    
    for platform, games in all_the_data[LOG_DATA][SAVED_IMAGE_PATHS].items():
        for game_title, game_paths in games.items():
            for game_path, media_types in game_paths.items():
                for media, save_data in media_types.items():
                    
                    if (pillow_installed and
                        all_the_data[LOG_DATA][IMAGE_EDITS][platform][game_title][game_path][media][save_data[IMAGE_OUTPUT]].get(ERROR)):
                            image_edit_errors += 1
                    if type(save_data[SAVE_INFO]) == int and save_data[SAVE_INFO] > NOT_SAVED:
                        image_files_saved += 1
                    elif type(save_data) != int:
                        image_save_errors += 1
    
    return formated_completion_time, launchbox_images_found, games_found_in_lb_ra, image_edit_errors, image_files_saved, image_save_errors


### Open a log file for viewing.
###     (log_file_path) Path to a log file.
###     --> Returns a [None]
def openLogFile(log_file_path):
    OpenFile(log_file_path)
    return None


### Script Starts Here
if __name__ == '__main__':
    print(sys.version)
    print('=================================')
    print('= LaunchBox Images              =')
    print('=  To RetroArch Thumbnails      =')
    print('=                   by JDHatten =')
    print('=================================')
    MIN_VERSION = (3,8,0)
    MIN_VERSION_STR = '.'.join([str(n) for n in MIN_VERSION])
    assert sys.version_info >= MIN_VERSION, f'This Script Requires Python v{MIN_VERSION_STR} or Newer'
    
    paths = sys.argv[1:]
    if not paths:
        paths = [ROOT_DIR]
    
    print('---------------------------------')
    if debug: print('[Debug Mode On]')
    all_the_data = changePreset(preset_options[selected_preset])
    if all_the_data:
        all_the_data = getLaunchBoxRetroArchData(all_the_data)
    print('---------------------------------')
    
    if not all_the_data:
        loop = False
    else:
        loop = True
    
    while loop:
        
        for path in paths:
            all_the_data = findLaunchBoxGameImages(path, all_the_data)
        
        print('\n---------------------------------')
        launchbox_images_found = all_the_data[LOG_DATA][IMAGES_FOUND]
        print(f'LaunchBox Images Found: {launchbox_images_found}')
        
        if launchbox_images_found:
            input(f'Start Creating RetroArch Thumbnails?')
            all_the_data = createRetroArchImagePaths(all_the_data)
            #all_the_data = createRetroArchThumbnailImages(all_the_data)
        
        (formated_completion_time, launchbox_images_found, games_found_in_lb_ra,
         image_edit_errors, image_files_saved, image_save_errors) = getLogNumbers(all_the_data)
        
        print(f'\nAmount of Game Files Found in Both LaunchBox and RetroArch: {games_found_in_lb_ra}')
        print(f'Total Usable LaunchBox Images Found: {launchbox_images_found}')
        print(f'Amount of RetroArch Images Saved: {image_files_saved}')
        print(f'Images Not Saved Due To Errors: {image_save_errors}')
        print(f'Images That Failed Editing*: {image_edit_errors}')
        print('*If an error happens while editing an image, it still keeps it\'s previous edits and can still be saved.')
        print(f'\nTime To Completion: {formated_completion_time}')
        
        try_again = loop_script
        loop = loop_script
        while try_again:
            drop = input('\nDrop another Game file or directory here or leave blank and press [Enter] to create a log file now: ')
            drop = drop.replace('"', '')
            path = Path(drop)
            if drop == '':
                loop = False
                try_again = False
            elif path.exists():
                paths = [path]
                try_again = False
            else:
                print(f'This is not an existing file or directory path: "{drop}"')
    
    if create_log_file and all_the_data:
        log_file_created = createLogFile(all_the_data)
        if log_file_created:
            print('--> Check log for more details.')
            openLogFile(log_file_created)
        else:
            print('No log file necessary.')
    elif all_the_data:
        print('Log file creation turned off.')

