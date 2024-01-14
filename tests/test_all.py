MAX_COLOR = 128

import os
import requests
from timeit import default_timer
import sys
from materialyoucolor.utils.color_utils import rgba_from_argb
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.hct import Hct
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.scheme.scheme_android import SchemeAndroid
from materialyoucolor.scheme.scheme import Scheme
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.scheme.scheme_content import SchemeContent
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_rainbow import SchemeRainbow
from materialyoucolor.scheme.scheme_fidelity import SchemeFidelity
from materialyoucolor.scheme.scheme_fruit_salad import SchemeFruitSalad
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from rich.console import Console
from rich.table import Table
from PIL import Image

rgba_to_hex = lambda rgba: "#{:02X}{:02X}{:02X}{:02X}".format(*map(round, rgba))

FILENAME = sys.argv[1]

if not os.path.isfile(FILENAME):
    print("Downloading test image file: ")
    with open(FILENAME, "wb") as file:
        file.write(
            requests.get(
                "https://unsplash.com/photos/u9tAl8WR3DI/download?ixid=M3wxMjA3fDB8MXx0b3BpY3x8NnNNVmpUTFNrZVF8fHx8fDJ8fDE3MDUyMDgwNjF8&force=true"
            ).content
        )
    print("Downloaded: ", FILENAME, os.path.exists(FILENAME))

console = Console()

start = default_timer()
image = Image.open(FILENAME)

pixel_len = image.width * image.height
image_data = image.getdata()
pixel_array = [image_data[_] for _ in range(0, pixel_len, int(sys.argv[2]))]
end = default_timer()
print("File open took : ", end - start, "secs")

start = default_timer()
colors = QuantizeCelebi(pixel_array, MAX_COLOR)
selected = Score.score(colors)
end = default_timer()

print("Color generation took : ", end - start, "secs\n")


if os.name == "nt":
    # UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-5: character maps to <undefined>
    exit(0)

print("All dominant colors ({}) :\n".format(MAX_COLOR))
pused_colors = 0

for color in colors.keys():
    rgb = rgba_from_argb(color)[:-1]
    print("\x1b[48;2;{};{};{}m    \x1b[0m".format(*rgb), end="")
    pused_colors += 1
    if pused_colors % 16 == 0:
        print()
print()

st = Table(title="Selected colors", title_justify="left")
st.add_column("Color")
st.add_column("RGB")
st.add_column("Occurance")

for color in selected:
    rgb = rgba_from_argb(color)
    __ = rgba_to_hex(rgb)[:-2]
    st.add_row(
        "[{}]██████[/{}]".format(__, __),
        str(rgb[:-1]),
        str(colors[color]),
    )
console.print(st)


def print_scheme(scheme_function, name):
    print()
    schemes = [scheme_function(rgb) for rgb in selected]
    ssct = Table(title=name, title_justify="left")
    ssct.add_column("Name")
    for rgb in selected:
        co = rgba_to_hex(rgba_from_argb(rgb))[:-2]
        ssct.add_column("[{}]██████[/{}]".format(co, co))

    for key in schemes[0].props.keys():
        __ = (key,)
        for scheme in schemes:
            color = rgba_to_hex(scheme.props[key])[:-2]
            __ += ("[{}]██████[/{}]".format(color, color),)
        ssct.add_row(*__)
    console.print(ssct)
    print()


SCHEMES = {
    Scheme.light: "Light Scheme",
    Scheme.dark: "Dark Scheme",
    SchemeAndroid.light: "Android Light Scheme",
    SchemeAndroid.dark: "Android Dark Scheme",
}

for s_f in SCHEMES.keys():
    print_scheme(s_f, SCHEMES[s_f])


print("\nDynamic Schemes from top color:\n")


def print_dynamic_scheme(scheme_class):
    print()
    color = rgba_to_hex(rgba_from_argb(selected[0]))[:-2]
    contrast = 0
    ssct = Table(title=str(scheme_class).split(".")[-1][:-2], title_justify="left")
    ssct.add_column("Color : [{}]██████[/{}]".format(color, color))
    ssct.add_column("Light")
    ssct.add_column("Dark")
    scheme_l = scheme_class(Hct.from_int(selected[0]), False, contrast)
    scheme_d = scheme_class(Hct.from_int(selected[0]), True, contrast)

    for color in vars(MaterialDynamicColors).keys():
        __ = getattr(MaterialDynamicColors, color)
        if hasattr(__, "get_hct"):
            ssct.add_row(
                color,
                "[{}]██████[/{}]".format(
                    *[rgba_to_hex(__.get_hct(scheme_l).to_rgba())[:-2]] * 2
                ),
                "[{}]██████[/{}]".format(
                    *[rgba_to_hex(__.get_hct(scheme_d).to_rgba())[:-2]] * 2
                ),
            )
    console.print(ssct)
    print()


[
    print_dynamic_scheme(s)
    for s in [
        SchemeTonalSpot,
        SchemeExpressive,
        SchemeFidelity,
        SchemeFruitSalad,
        SchemeMonochrome,
        SchemeNeutral,
        SchemeRainbow,
        SchemeVibrant,
        SchemeContent,
    ]
]
