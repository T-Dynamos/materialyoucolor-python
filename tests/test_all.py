from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
try:
    from materialyoucolor.scheme.scheme_cmf import SchemeCmf
    from materialyoucolor.quantize import celebi
except (ImportError, AttributeError):
    for mod in list(sys.modules.keys()):
        if mod == "materialyoucolor" or mod.startswith("materialyoucolor."):
            del sys.modules[mod]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

import psutil
from PIL import Image
from rich.console import Console
from rich.table import Table

from materialyoucolor.dynamiccolor.color_spec import COLOR_NAMES
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct.hct import Hct

# dynamic schemes
from materialyoucolor.scheme import *
from materialyoucolor.scheme.scheme_cmf import SchemeCmf

# non-dynamic scheme
from materialyoucolor.scheme.scheme import Scheme
from materialyoucolor.scheme.scheme_android import SchemeAndroid
from materialyoucolor.score.score import Score
from materialyoucolor.temperature.temperature_cache import TemperatureCache
from materialyoucolor.utils.color_utils import hex_from_rgba, rgba_from_argb

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
    "cmf": SchemeCmf,
}


def get_current_rss_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


# Regression: tone extremes leave TemperatureCache with a zero temperature range,
# which used to make complement raise ZeroDivisionError (issue #28).
def test_tone_extremes():
    for argb in [0xFFFFFFFF, 0xFF000000, 0xFF010101]:
        source = Hct.from_int(argb)
        assert TemperatureCache(source).complement.to_int() == source.to_int()
        for spec_version in ["2021", "2025", "2026"]:
            for is_dark in [False, True]:
                SchemeFidelity(source, is_dark, 0.0, spec_version=spec_version)


def test_smoke_all_schemes():
    source = Hct.from_int(0xFF4285F4)
    for name, scheme_cls in DYNAMIC_SCHEMES.items():
        for spec in ["2021", "2025", "2026"]:
            if scheme_cls == SchemeCmf and spec != "2026":
                continue
            s_l = scheme_cls(source, False, 0.0, spec_version=spec)
            s_d = scheme_cls(source, True, 0.0, spec_version=spec)
            assert s_l.primary_palette is not None
            assert s_d.primary_palette is not None


def main():
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
            except Exception:
                image_data = image.getdata()
            colors = QuantizeCelebi(
                [image_data[i] for i in range(0, pixel_len, args.quality)], MAX_COLOR
            )
            end = time.time()
            final_memory = get_current_rss_mb()
            print(f"Color[pillow] generation took {end - start:.4f} secs")
            print(f"Peak RAM usage (Pillow): {final_memory - initial_memory:.2f} MB")
        elif args.method == "cpp":
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
        colors = {
            0xFFFF0000: 100,  # Red
            0xFF00FF00: 500,  # Green
            0xFF0000FF: 25,  # Blue
            0xFFFFFF00: 75,  # Yellow
        }

    selected = Score.score(colors)

    test_tone_extremes()

    if os.name == "nt":
        return

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

    def print_scheme(scheme_function, name):
        print()
        schemes = [scheme_function(color_argb) for color_argb in selected]
        ssct = Table(title=name, title_justify="left")
        ssct.add_column("Name")
        for color_argb in selected:
            co = hex_from_rgba(rgba_from_argb(color_argb))[:-2]
            ssct.add_column("[{}]██████[/{}]".format(co, co))

        for key in schemes[0].to_json().keys():
            __ = (key,)
            for scheme in schemes:
                color = hex_from_rgba(rgba_from_argb(scheme.to_json()[key]))[:-2]
                __ += ("[{}]██████[/{}]".format(color, color),)
            ssct.add_row(*__)
        console.print(ssct)
        print()

    schemes_dict = {
        Scheme.light: "Light Scheme",
        Scheme.dark: "Dark Scheme",
        SchemeAndroid.light: "Android Light Scheme",
        SchemeAndroid.dark: "Android Dark Scheme",
    }

    for s_f in schemes_dict.keys():
        print_scheme(s_f, schemes_dict[s_f])

    print("\nDynamic Schemes from top color:\n")

    def print_dynamic_scheme(scheme_class):
        print()
        color = hex_from_rgba(rgba_from_argb(selected[0]))[:-2]
        contrast = 0
        ssct = Table(title=str(scheme_class).split(".")[-1][:-2], title_justify="left")
        ssct.add_column("Color : [{}]██████[/{}]".format(color, color))

        ssct.add_column("L(2021)")
        ssct.add_column("L(2025)")
        ssct.add_column("L(2026)")
        ssct.add_column("D(2021)")
        ssct.add_column("D(2025)")
        ssct.add_column("D(2026)")

        opts_l = [Hct.from_int(selected[0]), False, contrast]
        opts_d = [Hct.from_int(selected[0]), True, contrast]

        mdc2026 = MaterialDynamicColors(spec="2026")
        scheme_l_2026 = scheme_class(*opts_l, spec_version="2026")
        scheme_d_2026 = scheme_class(*opts_d, spec_version="2026")

        if scheme_class == SchemeCmf:
            scheme_l_2025 = None
            scheme_d_2025 = None
            scheme_l_2021 = None
            scheme_d_2021 = None
            mdc2025 = mdc2026
            mdc2021 = mdc2026
        else:
            mdc2025 = MaterialDynamicColors(spec="2025")
            scheme_l_2025 = scheme_class(*opts_l, spec_version="2025")
            scheme_d_2025 = scheme_class(*opts_d, spec_version="2025")

            mdc2021 = MaterialDynamicColors(spec="2021")
            scheme_l_2021 = scheme_class(*opts_l, spec_version="2021")
            scheme_d_2021 = scheme_class(*opts_d, spec_version="2021")

        get_color = lambda c, l: (
            "[{}]██████[/{}]".format(*[c.get_hex(l)[:-2]] * 2)
            if c is not None and l is not None
            else " NONE"
        )

        for color_name in COLOR_NAMES:
            c_2026 = getattr(mdc2026, color_name)
            c_2025 = getattr(mdc2025, color_name)
            c_2021 = getattr(mdc2021, color_name)
            ssct.add_row(
                color_name,
                get_color(c_2021, scheme_l_2021),
                get_color(c_2025, scheme_l_2025),
                get_color(c_2026, scheme_l_2026),
                get_color(c_2021, scheme_d_2021),
                get_color(c_2025, scheme_d_2025),
                get_color(c_2026, scheme_d_2026),
            )

        console.print(ssct)
        print()

    schemes_to_print = []
    if args.all or not any(
        getattr(args, name.replace("-", "_")) for name in DYNAMIC_SCHEMES.keys()
    ):
        schemes_to_print = list(DYNAMIC_SCHEMES.values())
    else:
        for name, scheme_class in DYNAMIC_SCHEMES.items():
            if getattr(args, name.replace("-", "_")):
                schemes_to_print.append(scheme_class)

    for s in schemes_to_print:
        print_dynamic_scheme(s)


if __name__ == "__main__":
    main()
