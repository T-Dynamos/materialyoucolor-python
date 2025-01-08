import json
import os
from glob import glob as path_find
import math
from timeit import default_timer

from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from materialyoucolor.scheme.scheme_fruit_salad import SchemeFruitSalad
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from materialyoucolor.scheme.scheme_rainbow import SchemeRainbow
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_fidelity import SchemeFidelity
from materialyoucolor.scheme.scheme_content import SchemeContent

from materialyoucolor.scheme.dynamic_scheme import DynamicSchemeOptions, DynamicScheme
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.utils.color_utils import argb_from_rgba_01, srgb_to_argb
from materialyoucolor.utils.math_utils import sanitize_degrees_double
from materialyoucolor.hct import Hct
from materialyoucolor.score.score import Score
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors

try:
    from materialyoucolor.quantize import QuantizeCelebi
except:
    QuantizeCelebi = None

autoclass = None
_is_android = "ANDROID_ARGUMENT" in os.environ

if _is_android:
    from jnius import autoclass
    from android import mActivity

    Integer = autoclass("java.lang.Integer")
    BuildVERSION = autoclass("android.os.Build$VERSION")
    context = mActivity.getApplicationContext()
    WallpaperManager = autoclass("android.app.WallpaperManager").getInstance(mActivity)

try:
    from PIL import Image
except Exception:
    Image = None

SCHEMES = {
    "TONAL_SPOT": SchemeTonalSpot,
    "SPRITZ": SchemeNeutral,
    "VIBRANT": SchemeVibrant,
    "EXPRESSIVE": SchemeExpressive,
    "FRUIT_SALAD": SchemeFruitSalad,
    "RAINBOW": SchemeRainbow,
    "MONOCHROME": SchemeMonochrome,
    "FIDELITY": SchemeFidelity,
    "CONTENT": SchemeContent,
}

OPTION_THEME_STYLE = "android.theme.customization.theme_style"
COLOR_NAMES = {
    "primary_palette": "system_accent1_{}",
    "secondary_palette": "system_accent2_{}",
    "tertiary_palette": "system_accent3_{}",
    "neutral_palette": "system_neutral1_{}",
    "neutral_variant_palette": "system_neutral2_{}",
}
APPROX_TONE = 200
APPROX_CHROMA = 50
DEFAULT_RESIZE_BITMAP_AREA = 112 * 112

WALLPAPER_CACHE = {}


def save_and_resize_bitmap(drawable, path):
    CompressFormat = autoclass("android.graphics.Bitmap$CompressFormat")
    FileOutputStream = autoclass("java.io.FileOutputStream")
    Bitmap = autoclass("android.graphics.Bitmap")
    BitmapConfig = autoclass("android.graphics.Bitmap$Config")
    Canvas = autoclass("android.graphics.Canvas")
    bitmap = Bitmap.createBitmap(
        drawable.getIntrinsicWidth(),
        drawable.getIntrinsicHeight(),
        BitmapConfig.ARGB_8888,
    )
    canvas = Canvas(bitmap)
    drawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight())
    drawable.draw(canvas)
    bitmap_area = bitmap.getWidth() * bitmap.getHeight()
    scale_ratio = -1

    if bitmap_area > DEFAULT_RESIZE_BITMAP_AREA:
        scale_ratio = math.sqrt(DEFAULT_RESIZE_BITMAP_AREA / bitmap_area)

    if scale_ratio >= 0:
        bitmap = Bitmap.createScaledBitmap(
            bitmap,
            math.ceil(bitmap.getWidth() * scale_ratio),
            math.ceil(bitmap.getHeight() * scale_ratio),
            False,
        )
    bitmap.compress(
        CompressFormat.PNG,
        100,
        FileOutputStream(path),
    )
    return bitmap.getWidth(), bitmap.getHeight()


def reverse_color_from_primary(color, scheme):
    # TODO: Find solution
    # Here we are using APPROX_TONE and APPROX_CHROMA
    # because information is lost.
    # Which likely will affect these colors:
    # primaryContainer, tertiaryContainer
    temp_hct = Hct.from_int(color)
    reversed_color = color
    if scheme in ["TONAL_SPOT", "SPRITZ", "VIBRANT", "RAINBOW", "CHROMA"]:
        reversed_color = Hct.from_hct(temp_hct.hue, APPROX_CHROMA, APPROX_TONE).to_int()
    elif scheme == "EXPRESSIVE":
        reversed_color = Hct.from_hct(
            sanitize_degrees_double(temp_hct.hue - 240.0), APPROX_CHROMA, APPROX_TONE
        ).to_int()
    elif scheme == "FRUIT_SALAD":
        reversed_color = Hct.from_hct(
            sanitize_degrees_double(temp_hct.hue + 50.0), APPROX_CHROMA, APPROX_TONE
        ).to_int()
    elif scheme in ["FIDELITY", "CONTENT"]:
        # We have chroma info same as source here!
        reversed_color = Hct.from_hct(
            temp_hct.hue, temp_hct.chroma, APPROX_TONE
        ).to_int()
    return reversed_color


def _get_android_12_above(
    logger, selected_scheme="TONAL_SPOT", contrast=0.0, dark_mode=False
) -> DynamicScheme:
    SettingsSecure = autoclass("android.provider.Settings$Secure")
    theme_settings = json.loads(
        SettingsSecure.getString(
            context.getContentResolver(),
            SettingsSecure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES,
        )
    )
    # Android 14 has this method
    try:
        contrast = mActivity.getSystemService(context.UI_MODE_SERVICE).getContrast()
        logger("Got contrast '{}'".format(contrast))
    except Exception:
        pass

    # See if system supports mutiple schemes
    if OPTION_THEME_STYLE in theme_settings.keys():
        selected_scheme = theme_settings[OPTION_THEME_STYLE]
        logger("Got system theme style '{}'".format(selected_scheme))

    # Get system colors
    get_system_color = lambda color_name: srgb_to_argb(
        context.getColor(
            context.getResources().getIdentifier(
                COLOR_NAMES[color_name].format(APPROX_TONE),
                "color",
                "android",
            )
        )
    )
    color_names = COLOR_NAMES.copy()
    for color_name in COLOR_NAMES.keys():
        hct = Hct.from_int(get_system_color(color_name))
        color_names[color_name] = TonalPalette.from_hue_and_chroma(hct.hue, hct.chroma)

    return DynamicScheme(
        DynamicSchemeOptions(
            reverse_color_from_primary(
                get_system_color("primary_palette"),
                selected_scheme,
            ),
            getattr(Variant, selected_scheme),
            contrast,
            dark_mode,
            **color_names,
        )
    )


def open_wallpaper_file(file_path) -> Image:
    try:
        return Image.open(file_path)
    except Exception:
        return None


def get_dynamic_scheme(
    # Scheme options
    dark_mode=True,
    contrast=0.0,
    dynamic_color_quality=10,
    # Fallbacks
    fallback_wallpaper_path=None,
    fallback_scheme_name="TONAL_SPOT",
    force_fallback_wallpaper=False,
    # Logging
    message_logger=print,
    logger_head="MaterialYouColor",
) -> DynamicScheme:
    logger = lambda message: message_logger(logger_head + " : " + message)

    selected_scheme = None
    selected_color = None

    if _is_android:
        # For Android 12 and 12+
        if BuildVERSION.SDK_INT >= 31:
            selected_scheme = _get_android_12_above(
                logger, selected_scheme, contrast, dark_mode
            )

        # For Android 8.1 and 8.1+
        elif BuildVERSION.SDK_INT >= 27:
            logger("Device doesn't supports MaterialYou")
            selected_color = argb_from_rgba_01(
                WallpaperManager.getWallpaperColors(WallpaperManager.FLAG_SYSTEM)
                .getPrimaryColor()
                .getComponents()
            )
            logger("Got top color from wallpaper '{}'".format(selected_color))

        # Lower than 8.1
        elif not force_fallback_wallpaper:
            logger(
                "Device does neither supports materialyoucolor "
                "nor provides pregenerated colors"
            )
            wallpaper_store_dir = context.getFilesDir().getAbsolutePath()
            wallpaper_file = ".wallpaper-{}.png".format(
                WallpaperManager.getWallpaperId(WallpaperManager.FLAG_SYSTEM)
            )
            fallback_wallpaper_path = os.path.join(wallpaper_store_dir, wallpaper_file)

            if not os.path.isfile(fallback_wallpaper_path):
                previous_files = path_find(
                    os.path.join(wallpaper_store_dir, ".wallpaper-*.png")
                )
                [os.remove(file) for file in previous_files]
                try:
                    # Requires `android.permission.READ_EXTERNAL_STORAGE` permission
                    wallpaper_drawable = WallpaperManager.getDrawable()
                    width, height = save_and_resize_bitmap(
                        wallpaper_drawable, fallback_wallpaper_path
                    )
                    logger(
                        "Resized the system wallpaper : '{}x{}'".format(width, height)
                    )
                except Exception as e:
                    logger("Failed to get system wallpaper : " + str(e))
                    fallback_wallpaper_path = None

    if all(
        [
            not selected_color,
            not selected_scheme,
            fallback_wallpaper_path in WALLPAPER_CACHE.keys()
            and WALLPAPER_CACHE[fallback_wallpaper_path][1]
            == os.path.getsize(fallback_wallpaper_path),
        ]
    ):
        logger(
            "Got wallpaper color from cache '{}'".format(
                WALLPAPER_CACHE[fallback_wallpaper_path][0]
            )
        )
        selected_color = WALLPAPER_CACHE[fallback_wallpaper_path][0]

    if (
        not selected_scheme
        and not selected_color
        and fallback_wallpaper_path
        and (image := open_wallpaper_file(fallback_wallpaper_path))
        and QuantizeCelebi is not None
    ):
        timer_start = default_timer()
        pixel_len = image.width * image.height
        image_data = image.getdata()
        # TODO: Think about getting data from bitmap
        pixel_array = [
            image_data[_]
            for _ in range(
                0, pixel_len, dynamic_color_quality if not _is_android else 1
            )
        ]
        logger(
            f"Created an array of pixels from a "
            f"system wallpaper file - {default_timer() - timer_start} sec."
        )
        timer_start = default_timer()
        colors = QuantizeCelebi(pixel_array, 128)
        selected_color = Score.score(colors)[0]
        WALLPAPER_CACHE[fallback_wallpaper_path] = [
            selected_color,
            os.path.getsize(fallback_wallpaper_path),
        ]
        logger(f"Got dominant colors - " f"{default_timer() - timer_start} sec.")

    return (
        (
            SCHEMES[fallback_scheme_name](
                Hct.from_int(selected_color),
                dark_mode,
                contrast,
            )
            if selected_color
            else None
        )
        if not selected_scheme
        else selected_scheme
    )
