# [Material You color algorithms](https://m3.material.io/styles/color/overview) for python!
It is built in reference with offical [typescript implementation](https://github.com/material-foundation/material-color-utilities/tree/main/typescript) except it's color quantization part, which is based on [c++ implementation](https://github.com/material-foundation/material-color-utilities/tree/main/cpp) thanks to [pybind](https://github.com/pybind).

## Features 

1. Up to date with `material-foundation/material-color-utilities`.
2. Uses official c++ sources for quantization backend, which makes color generation fast!

## Minimal running example:

Run file `tests/test_all.py` as:

```console
usage: test_all.py [-h] [--tonal-spot] [--expressive] [--fidelity] [--fruit-salad] [--monochrome] [--neutral] [--rainbow] [--vibrant]
                   [--content] [--all] [--image IMAGE] [--quality QUALITY] [--method {pillow,cpp}]

Material You Color Scheme Test

options:
  -h, --help            show this help message and exit
  --tonal-spot          Print the tonal-spot dynamic scheme
  --expressive          Print the expressive dynamic scheme
  --fidelity            Print the fidelity dynamic scheme
  --fruit-salad         Print the fruit-salad dynamic scheme
  --monochrome          Print the monochrome dynamic scheme
  --neutral             Print the neutral dynamic scheme
  --rainbow             Print the rainbow dynamic scheme
  --vibrant             Print the vibrant dynamic scheme
  --content             Print the content dynamic scheme
  --all                 Print all dynamic schemes (default)
  --image IMAGE         Path to an image file for color extraction
  --quality QUALITY     Quality for image quantization (default: 5)
  --method {pillow,cpp}
                        Method for color quantization (default: cpp)
```

<details>
    <summary>Click to view result</summary>

[Image Used, size was 8MB](https://unsplash.com/photos/zFMbpChjZGg/)

<img width="666" height="516" alt="image" src="https://github.com/user-attachments/assets/68bc415b-3eb5-41d4-96e3-f36ced7411a8" />


It is recommended to use the `cpp` backend, as the `pillow` backend is extremely memory-inefficient for large images.
Newer Pillow APIs such as `Image.get_flattened_data()` eagerly materialize the entire image into a full list,
so quality-based subsampling is applied only after full expansion and does not reduce memory usage.
While `Image.getdata()` allows sampling during iteration, it is deprecated.

The `cpp` backend avoids these issues by operating directly on compact pixel buffers.

</details>


## Usage

### Install

You can easily install it from pip by executing:
```console
pip3 install materialyoucolor --upgrade
```
Prebuilt binaries are avaliable for `linux`, `android`, `windows` and `macos`. If prebuilt binaries aren't available, then you should manually build and install.


### Build and install

```console
# Install 
pip3 install https://github.com/T-Dynamos/materialyoucolor-python/archive/master.zip

```
### OS Specific

#### Arch Linux (OUTDATED)

```console
yay -S python-materialyoucolor
```

Thanks :heart: to [@midn8hustlr](https://github.com/midn8hustlr) for this [AUR package](https://aur.archlinux.org/cgit/aur.git/?h=python-materialyoucolor-git).

#### Android (using kivy's [`buildozer`](https://github.com/kivy/buildozer))

Ensure these lines in `buildozer.spec`:
```python
requirements = materialyoucolor==3.0.2
p4a.branch = develop
```

#### IOS (using kivy's [`kivy-ios`](https://github.com/kivy/kivy-ios))

Install latest version of kivy-ios and use as:
```console
toolchain build materialyoucolor
```

## Usage examples
<details>
<summary> Click to show </summary>
    
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
from materialyoucolor.dynamiccolor.color_spec import COLOR_NAMES
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors

# There are 9 different variants of scheme.
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
# Others you can import: SchemeExpressive, SchemeFruitSalad, SchemeMonochrome, SchemeRainbow, SchemeVibrant, SchemeNeutral, SchemeFidelity and SchemeContent

# SchemeTonalSpot is android default
scheme = SchemeTonalSpot( # choose any scheme here
    Hct.from_int(0xff4181EE), # source color in hct form
    True, # dark mode
    0.0, # contrast
    spec_version="2025"
)

mdc = MaterialDynamicColors(spec="2025")

for color in COLOR_NAMES:
    _color = getattr(mdc, color)
    print(color, _color.get_rgba(scheme), _color.get_hex(scheme))

# background [13, 14, 18, 255] #0D0E12FF
# onBackground [227, 229, 240, 255] #E3E5F0FF
# surface [13, 14, 18, 255] #0D0E12FF
# surfaceDim [13, 14, 18, 255] #0D0E12FF
# surfaceBright [41, 44, 52, 255] #292C34FF
# surfaceContainerLowest [0, 0, 0, 255] #000000FF
# surfaceContainerLow [17, 19, 24, 255] #111318FF
# surfaceContainer [23, 25, 31, 255] #17191FFF
# surfaceContainerHigh [29, 31, 38, 255] #1D1F26FF
# surfaceContainerHighest [35, 38, 45, 255] #23262DFF
# onSurface [227, 229, 240, 255] #E3E5F0FF
# surfaceVariant [35, 38, 45, 255] #23262DFF
# onSurfaceVariant [196, 198, 208, 255] #C4C6D0FF
# outline [142, 144, 154, 255] #8E909AFF
...
```

- Generate and score colors from image

```python
from materialyoucolor.quantize import QuantizeCelebi, ImageQuantizeCelebi
from materialyoucolor.score.score import Score

# Pixel subsampling factor (quality = 1 processes all pixels)
quality = 1

# Run Celebi color quantization on an image.
# Returns a dict: {ARGB_color_int: population}
result = ImageQuantizeCelebi(
    "example.jpg",
    quality,
    128,  # maximum number of colors
)

print(result)

# Rank and select the best theme colors.
# Returns a list of ARGB color integers.
selected_colors = Score.score(result)

print(selected_colors)
# {4278911493: 276721,
# 4280550664: 164247, 
# 4280683034: 144830,
# ...
```
</details>


## Gallery

These are some libraries which use this library for color generattion.

* [`dots-hyprland`](https://github.com/end-4/dots-hyprland)

<img width="480" height="270" alt="image" src="https://github.com/user-attachments/assets/b08ca7ac-61a1-480f-852d-cad82590006b" />

* [`kde-material-you-colors`](https://github.com/luisbocanegra/kde-material-you-colors)

<img width="480" height="270" alt="image" src="https://images.pling.com/img/00/00/67/61/06/2136963/frame-51.png" />

* [`EarthFM CLONE`]

  
<img width="270" height="480" alt="516392752-7f8a2b2e-d81f-4c2c-8550-c55dea07c5bb" src="https://github.com/user-attachments/assets/50d9b837-4b49-44b9-9e47-8efd593a4550" />


> This is my private project where the theme colors change based on the album art.

## FAQ
    
1. How it is different from `avanisubbiah/material-color-utilities`?

This library is up to date, fast, and uses a hybrid system for image generation.
