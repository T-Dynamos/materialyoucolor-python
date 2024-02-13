![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/b29c17d1-6c02-4c07-9a72-5b0198034760)

# [Material You color algorithms](https://m3.material.io/styles/color/overview) for python!
It is built in reference with offical [typescript implementation](https://github.com/material-foundation/material-color-utilities/tree/main/typescript) except it's color quantization part, which is based on [c++ implementation](https://github.com/material-foundation/material-color-utilities/tree/main/cpp) thanks to [pybind](https://github.com/pybind).

## Features 

1. Up to date with `material-foundation/material-color-utilities/`.
2. Uses official c++ sources for quantization backend, which makes color generation fast!

## Minimal running example:

Run file `tests/test_all.py` as:

```console
python3 test_all.py <image path> <quality>

```
Maximum quality is `1` that means use all pixels, and quality number more than `1` means how many pixels to skip in between while reading, also you can see it as compression.

<details>
    <summary>Click to view result</summary>

[Image Used, size was 8MB](https://unsplash.com/photos/zFMbpChjZGg/)

![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/9d5374c9-00b4-4b70-b82a-6792dd5c910f)
![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/2edd819f-8600-4c82-a18a-3b759f63a552)


</details>


## Install

You can easily install it from pip by executing:
```console
pip3 install materialyoucolor --upgrade
```
Prebuilt binaries are avaliable for `linux`, `windows` and `macos`. If prebuilt binaries aren't available, then you should manually build and install.


## Build and install

```console
# Install 
pip3 install https://github.com/T-Dynamos/materialyoucolor-python/archive/develop.zip

```

## Usage examples

- Generate non dynamic colors

```python
from materialyoucolor.scheme import Scheme
from materialyoucolor.scheme.scheme_android import SchemeAndroid

# Color is a an int, which is made as:
# 0xff + hex_code (without #)
# Eg: 0xff + #4181EE = 0xff4181EE
# To convert hex to this form, do `int("0xff" + "<hex code>", 16)`
color = 0xff4181EE

print(Scheme.light(color).props)
print(Scheme.dark(color).props)
# Props is a dict, key is color name and value is rgba format list
# {'primary': [0, 90, 195, 255], 'onPrimary': ....

# Same way for android
print(SchemeAndroid.light(color).props)
print(SchemeAndroid.dark(color).props)
```

- Generate dynamic colors
```python
# Color in hue, chroma, tone form
from materialyoucolor.hct import Hct
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors

# There are 9 different variants of scheme.
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
# Others you can import: SchemeExpressive, SchemeFruitSalad, SchemeMonochrome, SchemeRainbow, SchemeVibrant, SchemeNeutral, SchemeFidelity and SchemeContent

# SchemeTonalSpot is android default
scheme = SchemeTonalSpot( # choose any scheme here
    Hct.from_int(0xff4181EE), # source color in hct form
    True, # dark mode
    0.0, # contrast
)

for color in vars(MaterialDynamicColors).keys():
    color_name = getattr(MaterialDynamicColors, color)
    if hasattr(color_name, "get_hct"): # is a color
        print(color, color_name.get_hct(scheme).to_rgba()) # print name of color and value in rgba format

# background [14, 20, 21, 255]
# onBackground [222, 227, 229, 255]
# surface [14, 20, 21, 255]
# surfaceDim [14, 20, 21, 255]
# ...
```

- Generate and score colors from image

```python
# Pillow is required to open image to array of pixels
from PIL import Image
# C++ QuantizeCelebi
from materialyoucolor.quantize import QuantizeCelebi
# Material You's default scoring of colors
from materialyoucolor.score.score import Score

# Open image 
image = Image.open("path_to_some_image.jpg")
pixel_len = image.width * image.height
image_data = image.getdata()

# Quality 1 means skip no pixels
quality = 1
pixel_array = [image_data[_] for _ in range(0, pixel_len, quality)]

# Run algorithm
result = QuantizeCelebi(pixel_array, 128) # 128 -> number desired colors, default 128
print(result)
# {4278722365: 2320, 4278723396: 2405, 4278723657: 2366,...
# result is a dict where key is
# color in integer form (which you can convert later), and value is population

print(Score.score(result))
# [4278722365, 4278723657]
# list of selected colors in integer form

```

## FAQ
    
1. How it is different from `avanisubbiah/material-color-utilities`?

See https://github.com/T-Dynamos/materialyoucolor-python/issues/3
