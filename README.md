# materialyoucolor-pyhton
Material You color algorithms for python (crossplatform)!

SEE : https://m3.material.io/styles/color/dynamic-color/overview

## How does it works?
Android performs the following steps to generate color schemes from a user's wallpaper.

1. The system detects the main colors in the selected wallpaper image and extracts a source color.

2. The system uses that source color to further extrapolate five key colors known as Primary, Secondary, Tertiary, Neutral, and Neutral variant.
> ![img](https://developer.android.com/static/develop/ui/views/theming/images/source-extraction.png)
> *Figure 1. Example of source color extraction from wallpaper image and extraction to five key colors*

3. The system interprets each key color into a tonal palette of 13 tones.
> ![img2](https://developer.android.com/static/develop/ui/views/theming/images/tonal-palettes.png)
> *Figure 2. Example of generating a given tonal palettes*

4. The system uses this single wallpaper to derive five different color schemes, which provides the basis for any light and dark themes.

SEE MORE: https://developer.android.com/develop/ui/views/theming/dynamic-colors

## Where to use this colors?

SEE : https://m3.material.io/styles/color/the-color-system/color-roles

## Install 

Always prefer master branch

```console
pip3 install https://github.com/T-Dynamos/materialyoucolor-pyhton/archive/main.zip

```
or 

```console
pip3 install materialyoucolor
```

## Documentation

Please see `example.py`, its well documented by AI.

## Example
Install [kivy](https://kivy.org),[pillow](https://github.com/python-pillow/Pillow), [kivymd](https://github.com/kivymd/kivymd) and then run `example.py` file.

> Make sure to edit variables in example.py file, like 
> ```
> IMAGE_FILE = "/home/tdynamos/Downloads/test.png"  # file
> ```


| Input | Output |
|---------|---------|
| ![Image 1](https://cdn.ytechb.com/wp-content/uploads/2021/09/Pixel-6-Pro-Plants-Wallpaper-7.webp) | ![Image 2](https://user-images.githubusercontent.com/68729523/232314900-58f281e4-3cf5-495e-a0dc-81ddc7f57e1f.png) |

See all tokens : https://m3.material.io/styles/color/the-color-system/tokens

## Credits
https://github.com/fengsp/color-thief-py/blob/master/colorthief.py

https://github.com/avanisubbiah/material-color-utilities
