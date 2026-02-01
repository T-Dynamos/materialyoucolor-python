import argparse
import os
import time

import psutil
from PIL import Image
from rich.console import Console
from rich.table import Table

from materialyoucolor.dynamiccolor.color_spec import COLOR_NAMES
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct.hct import Hct

# dynamic schemes
# import all schemes
from materialyoucolor.scheme import *

# non-dynamic scheme
from materialyoucolor.scheme.scheme import Scheme
from materialyoucolor.scheme.scheme_android import SchemeAndroid
from materialyoucolor.score.score import Score
from materialyoucolor.utils.color_utils import hex_from_rgba, rgba_from_argb


def get_current_rss_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


# from materialyoucolor.scheme.[]. import []
MAX_COLOR = 128

DYNAMIC_SCHEMES = {
    "tonal-spot": SchemeTonalSpot,
    "expressive": SchemeExpressive,
    "fidelity": SchemeFidelity,
    "fruit-salad": SchemeFruitSalad,
    "monochrome": SchemeMonochrome,
    "neutral": SchemeNeutral,
    "rainbow": SchemeRainbow,
    "vibrant": SchemeVibrant,
    "content": SchemeContent,
}

console = Console()

# Argument parsing
parser = argparse.ArgumentParser(description="Material You Color Scheme Test")
for scheme_name in DYNAMIC_SCHEMES.keys():
    parser.add_argument(
        f"--{scheme_name}",
        action="store_true",
        help=f"Print the {scheme_name} dynamic scheme",
    )
parser.add_argument(
    "--all", action="store_true", help="Print all dynamic schemes (default)"
)
parser.add_argument(
    "--image", type=str, help="Path to an image file for color extraction"
)
parser.add_argument(
    "--quality",
    type=int,
    default=5,
    help="Quality for image quantization (default: 5)",
)
parser.add_argument(
    "--method",
    type=str,
    choices=["pillow", "cpp"],
    default="cpp",
    help="Method for color quantization (default: cpp)",
)
args = parser.parse_args()

colors = {}
if args.image:
    if args.method == "pillow":
        from materialyoucolor.quantize import QuantizeCelebi

        print("########## PILLOW METHOD ##########")
        initial_memory = get_current_rss_mb()
        start = time.time()
        image = Image.open(args.image)
        pixel_len = image.width * image.height
        try:
            image_data = image.get_flattened_data()
        except:
            image_data = image.getdata()
        colors = QuantizeCelebi(
            [image_data[i] for i in range(0, pixel_len, args.quality)], MAX_COLOR
        )
        end = time.time()
        final_memory = get_current_rss_mb()
        print(f"Color[pillow] generation took {end - start:.4f} secs")
        print(f"Peak RAM usage (Pillow): {final_memory - initial_memory:.2f} MB")
    elif args.method == "cpp":
        # Import ImageQuantizeCelebi for C++ method
        from materialyoucolor.quantize import ImageQuantizeCelebi

        print("########## C++ Method ##########")
        initial_memory = get_current_rss_mb()
        start = time.time()
        colors = ImageQuantizeCelebi(args.image, args.quality, MAX_COLOR)
        end = time.time()
        final_memory = get_current_rss_mb()
        print(f"Color[stb_image] generation took {end - start:.4f} secs")
        print(f"Peak RAM usage (C++): {final_memory - initial_memory:.2f} MB")
else:
    # Since quantization is skipped, we need some default colors for testing.
    # Let's use some hardcoded colors for now.
    colors = {
        0xFFFF0000: 100,  # Red
        0xFF00FF00: 500,  # Green
        0xFF0000FF: 25,  # Blue
        0xFFFFFF00: 75,  # Yellow
    }


selected = Score.score(colors)

if os.name == "nt":
    exit(0)

print("All dominant colors ({}) :\n".format(MAX_COLOR))
pused_colors = 0

for color in colors.keys():
    rgb = rgba_from_argb(color)[:-1]
    print(
        "\x1b[48;2;{};{};{}m    \x1b[0m".format(
            round(rgb[0]), round(rgb[1]), round(rgb[2])
        ),
        end="",
    )
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
    st.add_row(
        "[{}]██████[/{}]".format(*[hex_from_rgba(rgb)[:-2]] * 2),
        str([round(c) for c in rgb[:-1]]),
        str(colors[color]),
    )
console.print(st)


# SKIP STATIC SCHEME
def print_scheme(scheme_function, name):
    print()
    schemes = [scheme_function(color_argb) for color_argb in selected]  # Pass ARGB int
    ssct = Table(title=name, title_justify="left")
    ssct.add_column("Name")
    for color_argb in selected:  # Use color_argb for clarity
        co = hex_from_rgba(rgba_from_argb(color_argb))[:-2]
        ssct.add_column("[{}]██████[/{}]".format(co, co))

    for key in schemes[0].to_json().keys():
        __ = (key,)
        for scheme in schemes:
            color = hex_from_rgba(rgba_from_argb(scheme.to_json()[key]))[
                :-2
            ]  # Ensure color is ARGB int
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

    color = hex_from_rgba(rgba_from_argb(selected[0]))[:-2]
    contrast = 0
    ssct = Table(title=str(scheme_class).split(".")[-1][:-2], title_justify="left")
    ssct.add_column("Color : [{}]██████[/{}]".format(color, color))

    ssct.add_column("L(2021)")
    ssct.add_column("L(2025)")
    ssct.add_column("D(2021)")
    ssct.add_column("D(2025)")

    opts_l = [Hct.from_int(selected[0]), False, contrast]
    opts_d = [Hct.from_int(selected[0]), True, contrast]

    mdc2025 = MaterialDynamicColors(spec="2025")
    scheme_l_2025 = scheme_class(*opts_l, spec_version="2025")
    scheme_d_2025 = scheme_class(*opts_d, spec_version="2025")

    mdc2021 = MaterialDynamicColors(spec="2021")
    scheme_l_2021 = scheme_class(*opts_l, spec_version="2021")
    scheme_d_2021 = scheme_class(*opts_d, spec_version="2021")

    get_color = lambda c, l: (
        "[{}]██████[/{}]".format(
            #           strip alpha from hex
            #               |
            #               V
            *[c.get_hex(l)[:-2]]
            * 2
        )
        if c is not None
        else " NONE"
    )

    for color in COLOR_NAMES:
        c_2025 = getattr(mdc2025, color)
        c_2021 = getattr(mdc2021, color)
        ssct.add_row(
            color,
            get_color(c_2021, scheme_l_2021),
            get_color(c_2025, scheme_l_2025),
            get_color(c_2021, scheme_d_2021),
            get_color(c_2025, scheme_d_2025),
        )

    console.print(ssct)
    print()


# Determine which schemes to print
schemes_to_print = []
if args.all or not any(
    getattr(args, name.replace("-", "_")) for name in DYNAMIC_SCHEMES.keys()
):
    schemes_to_print = DYNAMIC_SCHEMES.values()
else:
    for name, scheme_class in DYNAMIC_SCHEMES.items():
        if getattr(args, name.replace("-", "_")):
            schemes_to_print.append(scheme_class)

for s in schemes_to_print:
    print_dynamic_scheme(s)
