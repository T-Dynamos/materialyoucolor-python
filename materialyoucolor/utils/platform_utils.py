import json
import os
from glob import glob as path_find
import math

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
from materialyoucolor.hct import Hct
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors

try:
    from jnius import autoclass
    from android import mActivity
    from PIL import Image
except Exception:
    autoclass = None

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

DEFAULT_RESIZE_BITMAP_AREA = 112 * 112


def _is_android() -> bool:
    try:
        from android import mActivity
        return True
    except Exception as e:
        print("Platform does not seems to be android")
        pass
    return False


def save_and_resize_bitmap(drawable, path):
    CompressFormat = autoclass("android.graphics.Bitmap$CompressFormat")
    FileOutputStream = autoclass("java.io.FileOutputStream")
    Bitmap = autoclass("android.graphics.Bitmap")
    Canvas = autoclass("android.graphics.Canvas")
    bitmap = Bitmap.createBitmap(
        drawable.getIntrinsicWidth(),
        drawable.getIntrinsicHeight(),
        Bitmap.Config.ARGB_8888,
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
    return bitmap.getWidth(), bitmap.getHeight


def reverse_color_from_primary(color, scheme):
    reversed_color = color
    # if scheme == "TONAL_SPOT":
    #    temp_hct = Hct.from_int(color)

    return reversed_color


def get_scheme(
    wallpaper_path=None,
    fallback_scheme="TONAL_SPOT",
    dark_mode=True,
    contrast=0.0,
    dynamic_color_quality=10,
    message_logger=print,
    fallback_color=0xFF0000FF,
    logger_head="MaterialYouColor",
):
    is_android = _is_android()
    selected_color = None
    logger = lambda message: message_logger(logger_head + " : " + message)
    dynamic_scheme = None

    if is_android:
        Integer = autoclass("java.lang.Integer")
        BuildVERSION = autoclass("android.os.Build$VERSION")
        context = mActivity.getApplicationContext()
        WallpaperManager = autoclass("android.app.WallpaperManager").getInstance(
            mActivity
        )
        # For Android 12 and 12+
        if BuildVERSION.SDK_INT >= 31:
            logger("Device supports MaterialYou")
            SettingsSecure = autoclass("android.provider.Settings$Secure")
            theme_settings = json.loads(
                SettingsSecure.getString(
                    context.getContentResolver(),
                    SettingsSecure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES,
                )
            )
            # Android 14 has this method
            try:
                contrast = mActivity.getSystemService(
                    context.UI_MODE_SERVICE
                ).getContrast()
                logger("Got contrast '{}'".format(contrast))
            except Exception:
                pass

            if OPTION_THEME_STYLE in theme_settings.keys():
                fallback_scheme = theme_settings[OPTION_THEME_STYLE]
                logger("Got system theme style '{}'".format(fallback_scheme))

            color_names = COLOR_NAMES.copy()
            for color_name in list(COLOR_NAMES.keys())[::-1]:
                hct = Hct.from_int(
                    srgb_to_argb(
                        context.getColor(
                            context.getResources().getIdentifier(
                                color_names[color_name].format(100),
                                "color",
                                "android",
                            )
                        )
                    )
                )
                color_names[color_name] = TonalPalette.from_hue_and_chroma(
                    hct.hue, hct.chroma
                )

            dynamic_scheme = DynamicScheme(
                DynamicSchemeOptions(
                    # TODO: Get accurate source color
                    srgb_to_argb(
                        context.getColor(
                            context.getResources().getIdentifier(
                                COLOR_NAMES["primary_palette"].format(100),
                                "color",
                                "android",
                            )
                        )
                    ),
                    getattr(Variant, fallback_scheme),
                    contrast,
                    dark_mode,
                    **color_names
                )
            )

        # For Android 8.1 and 8.1+
        elif BuildVERSION.SDK_INT >= 27:
            logger("Device does not supports MaterialYou")
            selected_color = argb_from_rgba_01(
                WallpaperManager.getWallpaperColors(WallpaperManager.FLAG_SYSTEM)
                .getPrimaryColor()
                .getComponents()
            )
            logger("Got top color from wallpaper '{}'".format(selected_color))

        # Lower than 8.1
        else:
            logger(
                "Device does neither supports materialyoucolor"
                " nor provides pregenerated colors"
            )
            wallpaper_store_dir = context.getFilesDir().getAbsolutePath()
            wallpaper_file = ".wallpaper-{}.png".format(
                WallpaperManager.getWallpaperId(WallpaperManager.FLAG_SYSTEM)
            )
            wallpaper_path = os.path.join(wallpaper_store_dir, wallpaper_file)

            if not os.path.isfile(wallpaper_path):
                previous_files = path_find(
                    os.path.join(wallpaper_store_dir, ".wallpaper-*.png")
                )
                [os.remove(file) for file in previous_files]
                try:
                    wallpaper_drawable = WallpaperManager.getDrawable()
                    width, height = save_and_resize_bitmap(
                        wallpaper_drawable, wallpaper_path
                    )
                    logger(
                        "Got the system wallpaper with size: '{}x{}'".format(
                            width, height
                        )
                    )
                except Exception as e:
                    logger("Failed to get system wallpaper : " + str(e))
                    wallpaper_path = None

    if not selected_color and wallpaper_path:
        image = Image.open(wallpaper_path)
        pixel_len = image.width * image.height
        image_data = image.getdata()
        # TODO: Think about getting data from bitmap
        pixel_array = [
            image_data[_]
            for _ in range(0, pixel_len, dynamic_color_quality if not is_android else 1)
        ]
        colors = QuantizeCelebi(pixel_array, 128)
        selected_color = Score.score(colors)[0]
    elif not selected_color:
        logger("Using defined color '{}'".format(fallback_color))
        selected_color = fallback_color

    return (
        SCHEMES[fallback_scheme](
            Hct.from_int(selected_color),
            dark_mode,
            contrast,
        )
        if not dynamic_scheme
        else dynamic_scheme
    )
