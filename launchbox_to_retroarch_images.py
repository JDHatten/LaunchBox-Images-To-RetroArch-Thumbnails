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
    [] Create log file.
    [X] Search only known game extensions.
    [] Modify image size, rotation, etc.
    [] Find a way to match up LaunchBox and RetroArch databases/platforms, for faster searches.
    [] 

'''

# Installation root paths to both LaunchBox and RetroArch applications.
launchbox_root = r''
retroarch_root = r''

# A list of file extensions used when searching directories for game files.
# If any of your game file extensions are not included below, add them now.
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
    '.32x','.md',          # Sega Genesis
    '.cdi','.gdi',         # Sega Dreamcast
    '.gg',                 # Sega Game Gear
]

# This script will continue to run allowing the dropping of additional files or directories.
# Set this to False and this script will run once, do it's thing, and close
loop_script = True

# Create a log file that will record all the details of each new RetroArch thumbnail created.
# Note: New log file will overwrite old log file. Rename and save log file once open if you want
# to prevent it being overwritten.
create_log_file = True ## TODO

# Use different alternating images with multi-disc games if there's more than one image found.
# Only used if each disc of a game is added to RetroArch (and not a single m3u playlist).
# If set to False the same image will be used for each game disc.
alternating_boxart_images = False
alternating_title_images = True
alternating_gameplay_images = True ## TODO: make these preset options

# Overwrite existing RetroArch thumbnail images?
overwrite_retroarch_thumbnails = True ## TODO: make this a preset option

# You shouldn't have to edit this as it's only used to identify multi-disc game files.
# However, if you have some unique file naming conventions for your games and know how to
# use Regular Expressions, go for it.
# Note: The + are just added for readability.
# Examples: "(Disc 1 of 3)", "[CD2]", "(Game Disc 1)" etc
re_disc_info_pattern = ( '\s*' + '(\(|\[)' + '(CD|Disc|Disk|DVD|Game|Game\s*Disc)' +
                         '\s*(\d+)\s*\w*\s*(\d*)' + '(\)|\])' )

# Preset Options
DESCRIPTION = 0
FRONT_BOXART_PRIORITY = 1
TITLE_SCREEN_PRIORITY = 2
GAMEPLAY_SCREEN_PRIORITY = 3
MODIFY_IMAGE_WIDTH = 4
MODIFY_IMAGE_HEIGHT = 5
KEEP_ASPECT_RATIO = 6
SEARCH_SUB_DIRS = 10

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

# Extra Parameters
QUALITY = 0      ## TODO
SUBSAMPLING = 1
OPTIMIZE = 2
PROGRESSIVE = 3

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

### Select the default preset to use here. ###
selected_preset = 1

preset0 = { #              : Defaults                   # If option omitted, the default option value will be used.
  DESCRIPTION              : '',                        # Description of this preset.
  FRONT_BOXART_PRIORITY    : DEFAULT_FRONT_BOXARTS,     # A list of LaunchBox image categories (in order of priority)
  TITLE_SCREEN_PRIORITY    : DEFAULT_TITLE_SCREENS,     #   to use when selecting a front boxart, title screen, and
  GAMEPLAY_SCREEN_PRIORITY : DEFAULT_GAMEPLAY_SCREENS,  #   gameplay screen thumbnail for RetroArch.
  MODIFY_IMAGE_WIDTH       : NO_CHANGE,                 # Modify LaunchBox images before saving them as RetroArch thumbnails.
  MODIFY_IMAGE_HEIGHT      : NO_CHANGE,                 #   Example: ('Image Modifier', Number, 'Resampling Filter')
  KEEP_ASPECT_RATIO        : True,                      # Keep aspect ratio only if one size, width or height, has changed.
  SEARCH_SUB_DIRS          : False,                     # After searching for games in a directory also search sub-directories.
}                                                       # 

preset1 = {
  DESCRIPTION              : ('Front and back boxart with a gameplay image. '+
                              'And downscale image heights to 1080.'),
  TITLE_SCREEN_PRIORITY    : ['Box - Back',
                              'Box - Back - Reconstructed',
                              'Fanart - Box - Back',
                              'Screenshot - Game Title'],
  MODIFY_IMAGE_HEIGHT      : (DOWNSCALE, 1080, NEAREST), ## TODO
  KEEP_ASPECT_RATIO        : True,
  SEARCH_SUB_DIRS          : True
}

# Add any newly created presets to this preset_options List.
preset_options = [preset0,preset1]#,preset2,preset3,preset4]



####### Don't Edit Below This Line (unless you know what your doing) #######


# Extra log messages and images are saved in this script's root, not in RetroArch.
debug = False

import configparser
from datetime import datetime
import json
from pathlib import Path, PurePath
from PIL import Image, UnidentifiedImageError
from os import getenv, startfile as OpenFile, walk as Search
import re
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

NOT_SAVED = 0
#ERROR = 1
NEW_SAVE = 1
OVERWRITTEN = 2

# Image Dimensions
WIDTH = 0
HEIGHT = 1

# Image Modifier Indexes
MODIFIER = 0
NUMBER = 1

# Multi-Disc Regular Expression
re_disc_info_compiled_pattern = re.compile(re_disc_info_pattern, re.IGNORECASE)

# Regular Expression to get a number
re_number_pattern = re.compile('\d*\.?\d*', re.IGNORECASE)

# Characters not allowed in file names.
illegal_characters = list('\\|:"<>/?')


### Change the preset in use, retaining any log data.
###     (preset) A preset that holds the user options on how to copy and edit images.
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def changePreset(preset, all_the_data = {}):
    
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
    else:
        all_the_data[APP_DATA] = app_data
        all_the_data[LOG_DATA] = log_data
    
    #print(all_the_data)
    
    return all_the_data


### Get file data and existing paths to needed files and directories from LaunchBox and RetroArch.
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
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
    for app_name, app_path in {'LaunchBox' : launchbox_root ,'RetroArch' : retroarch_root}.items():
        
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
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def findLaunchBoxGameImages(path, all_the_data):
    search_sub_dirs = all_the_data.get(SEARCH_SUB_DIRS, False)
    paths = makeList(path)
    
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
    
    return all_the_data


### Search for the correct game images and record thier paths.
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
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
                        game_platform = game_data.find('Platform').text
                        game_title = game_data.find('Title').text
                        
                        if debug: print(f'  <ApplicationPath>{app_path}</ApplicationPath>')
                        if debug: print(f'  <Platform>{game_platform}</Platform>')
                        if debug: print(f'  <Title>{game_title}</Title>')
                        
                        if game_platform in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS]:
                            print(f'\nSearching for best image to use for a RetroArch Boxart thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, game_platform, game_title, FRONT_BOXART, DEFAULT_FRONT_BOXARTS)
                            print(f'\nSearching for best image to use for a RetroArch Title thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, game_platform, game_title, TITLE_SCREEN, DEFAULT_TITLE_SCREENS)
                            print(f'\nSearching for best image to use for a RetroArch Snap thumbnail...')
                            all_the_data = saveImagePaths(all_the_data, game_platform, game_title, GAMEPLAY_SCREEN, DEFAULT_GAMEPLAY_SCREENS)
                            
                            #print(all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform][IMAGE_PATHS][game_title])
                            
                            if game_title in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform].get(GAME_PATHS, {}):
                                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform][GAME_PATHS][game_title].append(game_path)
                            else:
                                all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform][GAME_PATHS].update({game_title : [game_path]})
                        
                        game_found = True
                        break
                
                if game_found: break
        if game_found: break
    
    return all_the_data


### Record and properly categorize images to later transfer to RetroArch.
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     (game_platform) Game platform string.
###     (game_title) Game title string.
###     (media) Key name of image category priority option.
###     (default_media) Default list of image categories.
###     --> Returns a [Dictionary]
def saveImagePaths(all_the_data, game_platform, game_title, media, default_media = {}):
    #game_path = all_the_data[LOG_DATA][CURRENT_GAME_PATH]
    #game_title_path = Path(PurePath().joinpath(game_path.parent, game_title))
    platform_data = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].get(game_platform)
    media_type_list = all_the_data.get(media, default_media)
    
    if not platform_data[IMAGE_PATHS].get(game_title):
        platform_data[IMAGE_PATHS][game_title] = {}
    
    # Use alternative images with multi-disc games
    if alternating_gameplay_images:
        existing_images = makeList(platform_data[IMAGE_PATHS][game_title].get(media, []))
    else:
        existing_images = []
    
    for media_type in media_type_list:
        for path_data in platform_data[ALL_MEDIA_TYPES]:
            #print(path_data[MEDIA_TYPE])
            
            if media_type == path_data[MEDIA_TYPE]:
                ## TODO: Image number pref? (01,02,...) also (search) Format/Extension pref?
                ## TODO: NEW in LaunchBox. "Game Title.<ID>-01"  Have to search with and without ID (from xml) to find images ??
                ## TODO: Region prefs?
                #file_name = f'{game_title.replace(":","_")}-01'
                
                partial_file_name = f'{game_title}'
                for ic in illegal_characters:
                    partial_file_name = partial_file_name.replace(ic,"_")
                
                image_file_path = searchImageDirectory(path_data[DIR_PATH], partial_file_name, existing_images)
                
                if image_file_path:
                    print(f'Found: {image_file_path}')
                    all_the_data[LOG_DATA][IMAGES_FOUND] += 1
                    
                    if existing_images:
                        existing_images.append(image_file_path)
                    
                    platform_data[IMAGE_PATHS][game_title].update(
                        { media : existing_images if existing_images else [image_file_path] }
                    )
                    
                    ## TODO: Log?
                    return all_the_data
    ## TODO: Log?
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
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def createRetroArchImagePaths(all_the_data):
    retroarch_thumbnails_root = all_the_data[APP_DATA][RETROARCH][THUMBNAILS_DIR_PATH]
    if debug: debug_thumbnails_root = Path(PurePath().joinpath(ROOT_DIR,'thumbnails'))
    
    start_time = datetime.now().timestamp()
    
    for game_platform, data in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].items():
        for game_title, media in data[IMAGE_PATHS].items():
            print('\nGame Title:')
            print(f'  {game_title}')
            print('Usable Front Boxart Images:')
            boxart_paths = ",\n  ".join([str(path) for path in media[FRONT_BOXART]])
            print(f'  {boxart_paths}')
            print('Usable Title Screen Images:')
            title_paths = ",\n  ".join([str(path) for path in media[TITLE_SCREEN]])
            print(f'  {title_paths}')
            print('Usable Gameplay Screen Images:')
            gameplay_paths = ",\n  ".join([str(path) for path in media[GAMEPLAY_SCREEN]])
            print(f'  {gameplay_paths}')
            
            game_paths = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform][GAME_PATHS][game_title]
            #print(f'Game Paths: {game_paths}')
            
            for root, dirs, files in Search(all_the_data[APP_DATA][RETROARCH][PLAYLISTS_DIR_PATH]):
                for file in files:
                    if Path(file).suffix == '.lpl':
                        
                        retroarch_playlist_path = Path(PurePath().joinpath(root, file))
                        
                        # Only search playlist files if they belong to the same platform.
                        ## TODO: option to search all, in case platform names are too different?
                        ## There are many different platforms, not sure how they all match up within LB and RA naming conventions.
                        ##                    'Sony Playstation' =?= 'Sony - PlayStation'
                        ##                  'Sony Playstation 2' =?= 'Sony - PlayStation 2'
                        ##                            'Sony PSP' =?= 'Sony - PlayStation Portable'
                        ##                        'Sega Genesis' =?= 'Sega - Mega Drive - Genesis'
                        ## 'Super Nintendo Entertainment System' =?= 'Nintendo - Super Nintendo Entertainment System'
                        ## Sony Playstation could match Sony Playstation 2
                        ## What if games are added to wrong platforms, ex. Sega 32X put in Sega Genesis
                        
                        ## it takes 10x more time to search though all 20 (8 are quite big) of my playlists
                        ## its only noticeable with a large amount of game files searched/dropped (100+)
                        
                        ## Create list of platforms that have different spellings between LaunchBox and RetroArch, with all possible related platforms
                        ## 'Sony PSP' : ['Sony - PlayStation Portable', '']
                        ## 'Sega Genesis' : ['Sega - Mega Drive - Genesis', 'Sega - 32X', 'Sega - Mega-CD - Sega CD']
                        ## Sega 32X, Sega CD, Sega CD 32X,
                        ## if not in above list -> if Nintendo found in string, remove 'Nintendo - ' else just remove '- '
                        #launchbox_platform_name = game_platform.casefold()
                        retroarch_platform_name = retroarch_playlist_path.stem
                        #retroarch_platform_name_match = retroarch_platform_name.replace(' - ',' ').casefold()
                        #if retroarch_platform_name_match.find(launchbox_platform_name) == -1:
                        #    continue
                        
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
                                    if media[FRONT_BOXART]:
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
                                            media[FRONT_BOXART],
                                            retroarch_front_boxart_path,
                                            game_platform, game_title, FRONT_BOXART
                                        )
                                    if media[TITLE_SCREEN]:
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
                                            media[TITLE_SCREEN],
                                            retroarch_title_screen_path,
                                            game_platform, game_title, TITLE_SCREEN
                                        )
                                    if media[GAMEPLAY_SCREEN]:
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
                                            media[GAMEPLAY_SCREEN],
                                            retroarch_gameplay_screen_path,
                                            game_platform, game_title, GAMEPLAY_SCREEN
                                        )
                        
                        # Close RetroArch Playlist File
                        retroarch_playlist_file.close()
                
                break # Ignore Sub-Directories
    
    end_time = datetime.now().timestamp()
    completion_time = end_time - start_time
    #timestamp = datetime.now().timestamp()
    #date_time = datetime.fromtimestamp(timestamp)
    time = datetime.fromtimestamp(completion_time)
    #str_date_time = date_time.strftime('On %m/%d/%Y at %I:%M:%S %p')
    #str_date_time_file_name = date_time.strftime('%Y-%m-%d_%H.%M.%S')
    str_completion_time = time.strftime('%S.%f')
    if debug: print(str_completion_time)
    
    return all_the_data


### TODO
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     --> Returns a [Dictionary]
def createRetroArchThumbnailImages(all_the_data, image_source_paths, image_output_path, game_platform, game_title, media):
    
    ## TODO: do thumbnail creation all at once, on command?
    '''for game_platform, data in all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS].items():
        for game_title, image_path_data in data[IMAGE_PATHS].items():
            print(f'\nFront Boxart: {image_path_data[FRONT_BOXART]}')
            print(f'Title Screen: {image_path_data[TITLE_SCREEN]}')
            print(f'Gameplay Screen: {image_path_data[GAMEPLAY_SCREEN]}')
            game_paths = all_the_data[APP_DATA][LAUNCHBOX][PLATFORMS][game_platform][GAME_PATHS][game_title]
            
            for game_path in game_paths:
                # Check if game is also in RetroArch (true if image paths were created)
                if all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS].get(game_path):
                    
                    for media, image_source_paths in image_path_data.items():
                        image_output_path = all_the_data[APP_DATA][RETROARCH][IMAGE_PATHS][game_path][media]
    '''
    
    current_game_image_logs = all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][game_platform].get(game_title)
    if not current_game_image_logs:
        current_game_image_logs = all_the_data[LOG_DATA][SAVED_IMAGE_PATHS][game_platform][game_title] = {
            FRONT_BOXART : {}, TITLE_SCREEN : {}, GAMEPLAY_SCREEN : {}
            ## TODO: FRONT_BOXART : { CURRENT_GAME_PATH : [image_source_path, image_output_path, file_saved] }
        }
    
    # Get next image from source list
    next_alt_image = 0
    if len(image_source_paths) > 1:
        if media == FRONT_BOXART:
            use_image_alt = alternating_boxart_images
        elif media == TITLE_SCREEN:
            use_image_alt = alternating_title_images
        elif media == GAMEPLAY_SCREEN:
            use_image_alt = alternating_gameplay_images
        else:
            use_image_alt = False
        if use_image_alt and current_game_image_logs.get(media):
            for saved in current_game_image_logs.get(media, {}).values():
                if type(saved) == int and saved > 0:
                    next_alt_image += 1
                    # Start over and repeat if max hit
                    while next_alt_image >= len(image_source_paths):
                        next_alt_image -= len(image_source_paths)
    
    image_source_path = image_source_paths[next_alt_image]
    ## TODO: add image_source_path to log?
    
    if image_output_path.exists() and overwrite_retroarch_thumbnails:
        image_source = Image.open(image_source_path)
    elif not image_output_path.exists():
        image_source = Image.open(image_source_path)
    else:
        image_source = None
    
    #if image_source:
        ## TODO:
        ## modify image before saving
        ## Log: all_the_data[LOG_DATA][IMAGE_EDITS][game_platform][game_title]
        ## FRONT_BOXART : { image_output_path : [orginal_size, new_size, errors] }
    
    if image_output_path.exists():
        if overwrite_retroarch_thumbnails:
            file_saved = OVERWRITTEN
            image_output_path.unlink(missing_ok=True) # Delete
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
    
    current_game_image_logs[media].update({
        image_output_path : file_saved
    })
    
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
                percent_number = re_number_pattern.search(image_size_modifications[WIDTH][NUMBER])
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
                percent_number = re_number_pattern.search(image_size_modifications[HEIGHT][NUMBER])
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
###     (all_the_data) A Dictionary of all the details on what images to find and how to handle them with logs of everything done so far.
###     (log_file_path) Path of a log file.
###     --> Returns a [Boolean]
def createLogFile(all_the_data, log_file_path = None):
    ## TODO
    return False


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
    
    ROOT_DIR = Path(__file__).parent
    
    paths = sys.argv[1:]
    if not paths:
        paths = [ROOT_DIR]
    
    print('---------------------------------')
    if debug: print('[Debug Mode On]')
    all_the_data = changePreset(preset_options[selected_preset])
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
        
        ## TODO
        #games_found_in_lb_ra, launchbox_images_found, image_files_saved, image_edit_errors, image_save_errors = getLogNumbers(all_the_data)
        
        games_found_in_lb_ra = len(all_the_data[LOG_DATA][GAME_PATHS_IN_LB_RA])
        image_files_saved = 0
        for platform, games in all_the_data[LOG_DATA][SAVED_IMAGE_PATHS].items():
            for game_title, media_types in games.items():
                for media, path_data in media_types.items():
                    for path, save_results in path_data.items():
                        if type(save_results) == int and save_results > 0:
                            image_files_saved += 1
        
        print(f'\nAmount of Game Files Found in Both LaunchBox and RetroArch: {games_found_in_lb_ra}')
        print(f'Total Usable LaunchBox Images Found: {launchbox_images_found}')
        print(f'Amount of RetroArch Images Saved: {image_files_saved}')
        #print(f'Images Not Saved Due To Errors: {image_save_errors}')
        #print(f'Images That Failed Editing*: {image_edit_errors}')
        #print('*If an error happens while editing an image, it still keeps it\'s previous edits and can still be saved.')
        
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
    
    if create_log_file:
        log_file_created = createLogFile(all_the_data)
        if log_file_created:
            print('--> Check log for more details.')
            openLogFile(log_file_created)
        else:
            print('No log file necessary.')
    else:
        print('Log file creation turned off.')

