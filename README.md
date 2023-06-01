# LaunchBox-Images-To-RetroArch-Thumbnails

#### This script will copy images from LaunchBox and add them to RetroArch's thumbnails. With options to choose which LaunchBox images to prioritize for each of RetroArch's three thumbnail types 'Front Boxart', 'Title Screen', and 'Gameplay Screen' (AKA Named_Boxarts, Named_Titles, Named_Snaps).

<br>

## How To Use:
Drag and drop one or more game files or directories onto this script -or- run the script in a root game directory.

<br>

## How It Works:
When the script reads a known game file (ROM, Disc, etc.) and it's listed in both LaunchBox and RetroArch playlists, it will start copying images based on the options in a `preset`. Details of those options are listed below.

<br>

#### Image Category Priorities:
The first important options are image category priorities. Each representing one of three RetroArch thumbnail image types.

*Defaults*:
```
FRONT_BOXART_PRIORITY    : ['Box - Front','Box - Front - Reconstructed','Fanart - Box - Front','Box - 3D']
TITLE_SCREEN_PRIORITY    : ['Screenshot - Game Title','Screenshot - Game Select','Screenshot - High Scores','Screenshot - Game Over','Screenshot - Gameplay']
GAMEPLAY_SCREEN_PRIORITY : ['Screenshot - Gameplay','Screenshot - Game Select','Screenshot - Game Over','Screenshot - High Scores','Screenshot - Game Title']
```

*All LaunchBox Image Categories*:
```
"Advertisement Flyer - Back"
"Advertisement Flyer - Front"
"Amazon Background"
"Amazon Poster"
"Amazon Screenshot"
"Arcade - Cabinet"
"Arcade - Circuit Board"
"Arcade - Control Panel"
"Arcade - Controls Information"
"Arcade - Marquee"
"Banner"
"Box - 3D"
"Box - Back"
"Box - Back - Reconstructed"
"Box - Front"
"Box - Front - Reconstructed"
"Box - Full"
"Box - Spine"
"Cart - 3D"
"Cart - Back"
"Cart - Front"
"Clear Logo"
"Disc"
"Epic Games Background"
"Epic Games Poster"
"Epic Games Screenshot"
"Fanart - Background"
"Fanart - Box - Back"
"Fanart - Box - Front"
"Fanart - Cart - Back"
"Fanart - Cart - Front"
"Fanart - Disc"
"GOG Poster"
"GOG Screenshot"
"Origin Background"
"Origin Poster"
"Origin Screenshot"
"Screenshot - Game Over"
"Screenshot - Game Select"
"Screenshot - Game Title"
"Screenshot - Gameplay"
"Screenshot - High Scores"
"Steam Banner"
"Steam Poster"
"Steam Screenshot"
"Uplay Background"
"Uplay Thumbnail"
```

<br>

#### Region Priority:
Once an image category is selected the region is auto-detected and images are first selected from that region or related regions. Check the `auto_region_detector` setting for more details. Use the preset option `REGION_PRIORITY` if you want to change the *default* region priorities from English speaking regions to other regions.  Note: "Region Free" are simply images that aren’t located in specific LaunchBox region folders, but instead the root folder.<br>

*Default Region Priorities*:
```
REGION_PRIORITY : ['Region Free',
                   'North America',
                   'United States',
                   'United States, Europe',
                   'United States, Europe, Brazil',
                   'United States, Australia',
                   'United States, Japan',
                   'United States, Japan, Europe',
                   'United States, Korea',
                   'United States, Brazil',
                   'World',
                   'Europe',
                   'Europe, Japan',
                   'Australia',
                   'Canada',
                   'Japan',
                   'Japan, Korea',
                   'Asia',
                   'Oceania',
                   'South America',
                   'Brazil',
                   'China',
                   'Finland',
                   'France',
                   'Germany',
                   'Greece',
                   'Holland',
                   'Hong Kong',
                   'Italy',
                   'Korea',
                   'Norway',
                   'Russia',
                   'Spain',
                   'Sweden',
                   'Taiwan',
                   'The Netherlands']
```

<br>

#### Image Modification:
Next once all images are selected you can modify the images before saving them in RetroArch.

```
MODIFY_IMAGE_WIDTH  : ('Modifier', Number)
MODIFY_IMAGE_HEIGHT : ('Modifier', Number)
```
> Modifiers: `CHANGE_TO`, `MODIFY_BY_PIXELS`, `MODIFY_BY_PERCENT`, `UPSCALE`, `DOWNSCALE`

```
IMAGE_RESAMPLING_FILTER : NEAREST*, BILINEAR, or BICUBIC
```
> Resampling changes the total number of pixels in an image.

```
KEEP_ASPECT_RATIO : True* or False
```
> If only one size, width or height, has changed keep the aspect ratio with no distortion.

<br>

#### Other Options:

```
ALTERNATE_BOXART_IMAGES   : True, False*, or RANDOM
ALTERNATE_TITLE_IMAGES    : True, False*, or RANDOM
ALTERNATE_GAMEPLAY_IMAGES : True*, False, or RANDOM
```
> Use different alternating images with games that have additional discs, regions, versions, hacks, etc. Only used if there is more than one image found. If set to False the same image will be used for each game file.

```
FORMAT_PREFERENCE : JPG or PNG
```
> LaunchBox image format selection preference, '.png' or '.jpg'. LaunchBox only allows JPEG or PNG image files and RetroArch only allows PNG image files so JPEG images will be converted to PNG (if Pillow is installed).

```
PREFERRED_BOXART_NUMBER   : 1*-999
PREFERRED_TITLE_NUMBER    : 1*-999
PREFERRED_GAMEPLAY_NUMBER : 1*-999
```
> Every image in LaunchBox has a number (GameTitle-##.jpg) to distinguish it from other images in the same category/region. These options will use that preferred number first, and only use others if either the preferred number isn't found or is already selected in a game with multiple files (discs, regions, etc.). Has priority over ALTERNATE__IMAGES.

```
SEARCH_SUB_DIRS : True or False*
```
> After searching for games in a directory also search it's sub-directories.

```
OVERWRITE_IMAGES : True or False*
```
> Overwrite RetroArch thumbnail images, else skip the images that already exist.

<br>

\* = Default

<br>

#### Preset Examples:

```
preset1 = {
  DESCRIPTION               : 'Front and back boxart with a random gameplay image. And image heights downscaled to 1080.',
  TITLE_SCREEN_PRIORITY     : ['Box - Back',
                               'Box - Back - Reconstructed',
                               'Fanart - Box - Back',
                               'Screenshot - Game Title'],
  ALTERNATE_GAMEPLAY_IMAGES : RANDOM,
  MODIFY_IMAGE_HEIGHT       : (DOWNSCALE, 1080),
  KEEP_ASPECT_RATIO         : True,
  SEARCH_SUB_DIRS           : True,
  OVERWRITE_IMAGES          : True
}
```
```
preset2 = {
  DESCRIPTION               : 'Front (3D) boxart only, with height set to 720.',
  FRONT_BOXART_PRIORITY     : ['Box - 3D',
                               'Box - Front',
                               'Box - Front - Reconstructed',
                               'Fanart - Box - Front'],
  TITLE_SCREEN_PRIORITY     : SKIP,
  GAMEPLAY_SCREEN_PRIORITY  : SKIP,
  MODIFY_IMAGE_HEIGHT       : (CHANGE_TO, 720),
  IMAGE_RESAMPLING_FILTER   : BICUBIC,
  KEEP_ASPECT_RATIO         : True,
  SEARCH_SUB_DIRS           : True,
  OVERWRITE_IMAGES          : True
}
```

Once a preset is created fist add it to the `preset_options` List (in order).  Then select which preset to use by updating `selected_preset`.
