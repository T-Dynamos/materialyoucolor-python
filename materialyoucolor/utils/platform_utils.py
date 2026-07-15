import json
import math
import os
from glob import glob as path_find
from timeit import default_timer

from materialyoucolor.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.dynamiccolor.dynamic_scheme import (
    DynamicScheme,
)
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.scheme.scheme_content import SchemeContent
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from materialyoucolor.scheme.scheme_fidelity import SchemeFidelity
from materialyoucolor.scheme.scheme_fruit_salad import SchemeFruitSalad
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_rainbow import SchemeRainbow
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.score.score import Score
from materialyoucolor.utils.color_utils import argb_from_rgba_01, srgb_to_argb
from materialyoucolor.utils.math_utils import sanitize_degrees_double

try:
    from materialyoucolor.quantize import ImageQuantizeCelebi
except:
    ImageQuantizeCelebi = None


class MiniLogger:
    def info(self, message):
        print(f"[INFO] : {message}")

    def warning(self, message):
        print(f"[WARNING] : {message}")

    def error(self, message):
        print(f"[ERROR] : {message}")


autoclass = None
_is_android = "ANDROID_ARGUMENT" in os.environ

if _is_android:
    from android import mActivity
    from jnius import autoclass

    Integer = autoclass("java.lang.Integer")
    BuildVERSION = autoclass("android.os.Build$VERSION")
    context = mActivity.getApplicationContext()
    WallpaperManager = autoclass("android.app.WallpaperManager").getInstance(mActivity)

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


def reverse_color_from_primary(color, scheme) -> Hct:
    # TODO: Find solution
    # Here we are using APPROX_TONE and APPROX_CHROMA
    # because information is lost.
    # Which likely will affect these colors:
    # primaryContainer, tertiaryContainer
    temp_hct = Hct.from_int(color)
    reversed_color = temp_hct
    if scheme in ["TONAL_SPOT", "SPRITZ", "VIBRANT", "RAINBOW", "CHROMA"]:
        reversed_color = Hct.from_hct(temp_hct.hue, APPROX_CHROMA, APPROX_TONE)
    elif scheme == "EXPRESSIVE":
        reversed_color = Hct.from_hct(
            sanitize_degrees_double(temp_hct.hue - 240.0), APPROX_CHROMA, APPROX_TONE
        )
    elif scheme == "FRUIT_SALAD":
        reversed_color = Hct.from_hct(
            sanitize_degrees_double(temp_hct.hue + 50.0), APPROX_CHROMA, APPROX_TONE
        )
    elif scheme in ["FIDELITY", "CONTENT"]:
        # We have chroma info same as source here!
        reversed_color = Hct.from_hct(temp_hct.hue, temp_hct.chroma, APPROX_TONE)
    return reversed_color


def _get_android_12_above(
    logger,
    selected_scheme="TONAL_SPOT",
    contrast=0.0,
    dark_mode=False,
) -> DynamicScheme:

    theme_settings = {}

    # some examples of settings:

    # Product: A001T (Nothing 3a Lite)
    # Manufacturer: Nothing
    # {
    # android.theme.customization.system_palette:333333,
    # android.theme.customization.accent_color:333333,
    # _applied_timestamp:1749624776561,
    # android.theme.customization.color_source:preset,
    # android.theme.customization.color_index:1,
    # android.theme.customization.theme_style:MONOCHROMATIC
    # }
    # Issue: Quotes broken for some reason

    #  Product: A015 (CMF Phone 1)
    # Manufacturer: Nothing
    # {
    # "_applied_timestamp":1751394230432,
    # "android.theme.customization.system_palette":"6E4EA1",
    # "android.theme.customization.accent_color":"6E4EA1",
    # "android.theme.customization.color_source":"preset",
    # "android.theme.customization.color_index":"8",
    # "android.theme.customization.theme_style":"TONAL_SPOT"
    # }
    # Issue: None

    # Product: RMX2189 (Realme 12C)
    # Manufacturer: realme
    # Not supports MaterialYou

    try:
        SettingsSecure = autoclass("android.provider.Settings$Secure")
        settings_text = SettingsSecure.getString(
            context.getContentResolver(),
            SettingsSecure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES,
        )
        logger.info(f"Android settings data: '{settings_text}'")

        try:
            theme_settings = json.loads(settings_text)
        except:
            logger.info(f"Trying to read settings using fallback method")
            theme_settings = dict(
                item.split(":", 1) for item in settings_text.strip("{}").split(",")
            )
    except Exception as e:
        logger.warning(f"Parse [] error occured: {e}")

    # Android 14 has this method
    try:
        contrast = mActivity.getSystemService(context.UI_MODE_SERVICE).getContrast()
        logger.info(f"Got contrast '{contrast}'")
    except Exception:
        pass

    # See if system supports mutiple schemes
    if OPTION_THEME_STYLE in theme_settings.keys():
        selected_scheme = theme_settings[OPTION_THEME_STYLE]
        logger.info(f"Got system theme style '{selected_scheme}'")

    if selected_scheme == "MONOCHROMATIC":
        selected_scheme = "MONOCHROME"

    try:
        getattr(Variant, selected_scheme)
    except:
        logger.warning(
            f"invalid value for scheme: {selected_scheme} falling back to `TONAL_SPOT`"
        )
        selected_scheme = "TONAL_SPOT"

    # Get system colors
    def get_system_color(color_name):
        return srgb_to_argb(
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
        reverse_color_from_primary(
            get_system_color("primary_palette"),
            selected_scheme,
        ),
        getattr(Variant, selected_scheme),
        contrast,
        dark_mode,
        **color_names,
    )


def get_dynamic_scheme(
    # Scheme options
    dark_mode=True,
    contrast=0.0,
    dynamic_color_quality=10,
    spec_version="2025",
    # Fallbacks
    fallback_wallpaper_path=None,
    fallback_scheme_name="TONAL_SPOT",
    fallback_color=[25, 118, 210, 255],
    force_fallback_wallpaper=False,
    # Logging
    logger=None,
    logger_head="MaterialYouColor",
) -> DynamicScheme:

    class _Log:
        def __init__(self, logger, head):
            self._logger = logger if logger is not None else MiniLogger()
            self._head = head
        def info(self, m): self._logger.info(f"{self._head}: {m}")
        def warning(self, m): self._logger.warning(f"{self._head}: {m}")
        def error(self, m): self._logger.error(f"{self._head}: {m}")

    logger = _Log(logger, logger_head)

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
            logger.info("Device doesn't supports MaterialYou")
            try:
                selected_color = argb_from_rgba_01(
                    WallpaperManager.getWallpaperColors(WallpaperManager.FLAG_SYSTEM)
                    .getPrimaryColor()
                    .getComponents()
                )
                logger.info(f"Got top color from wallpaper '{selected_color}'")
            except Exception as e:
                logger.error(f"Failed to get wallpaper color: {e}")

        # Lower than 8.1
        elif not force_fallback_wallpaper:
            logger.info(
                "Device does neither supports materialyoucolor "
                "nor provides pregenerated colors"
            )
            try:
                wallpaper_store_dir = context.getFilesDir().getAbsolutePath()
                wallpaper_id = WallpaperManager.getWallpaperId(
                    WallpaperManager.FLAG_SYSTEM
                )
                wallpaper_file = f".wallpaper-{wallpaper_id}.png"
                fallback_wallpaper_path = os.path.join(
                    wallpaper_store_dir, wallpaper_file
                )

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
                        logger.info(
                            f"Resized the system wallpaper : '{width}x{height}'"
                        )
                    except Exception as e:
                        logger.error(f"Failed to get system wallpaper : {e}")
                        fallback_wallpaper_path = None
            except Exception as e:
                logger.error(f"Failed to access wallpaper directory: {e}")
                fallback_wallpaper_path = None

    if fallback_wallpaper_path and not os.path.isfile(fallback_wallpaper_path):
        logger.warning(f"wallpaper file '{fallback_wallpaper_path}' not found")

    if (
        fallback_wallpaper_path
        and os.path.isfile(fallback_wallpaper_path)
        and all(
            [
                not selected_color,
                not selected_scheme,
                fallback_wallpaper_path in WALLPAPER_CACHE.keys()
                and WALLPAPER_CACHE[fallback_wallpaper_path][1]
                == os.path.getsize(fallback_wallpaper_path),
            ]
        )
    ):
        logger.info(
            f"Got wallpaper color from cache '{WALLPAPER_CACHE[fallback_wallpaper_path][0]}'"
        )
        selected_color = WALLPAPER_CACHE[fallback_wallpaper_path][0]

    if (
        not selected_scheme
        and not selected_color
        and fallback_wallpaper_path
        and os.path.isfile(fallback_wallpaper_path)
        and ImageQuantizeCelebi is not None
    ):
        timer_start = default_timer()
        colors = ImageQuantizeCelebi(
            fallback_wallpaper_path, dynamic_color_quality, 128
        )
        selected_color = Score.score(colors)[0]
        WALLPAPER_CACHE[fallback_wallpaper_path] = [
            selected_color,
            os.path.getsize(fallback_wallpaper_path),
        ]

        logger.info(f"Got dominant colors - {default_timer() - timer_start} sec.")

    if not selected_scheme and not selected_color and fallback_color is not None:
        if isinstance(fallback_color, (list, tuple)) and len(fallback_color) >= 3:
            from materialyoucolor.utils.color_utils import argb_from_rgba

            rgba = [int(c) for c in fallback_color[:4]]
            if len(rgba) == 3:
                rgba.append(255)
            selected_color = argb_from_rgba(rgba)
        elif isinstance(fallback_color, str) and fallback_color.startswith("#"):
            from materialyoucolor.utils.color_utils import argb_from_rgb

            selected_color = argb_from_rgb(
                int(fallback_color[1:3], 16),
                int(fallback_color[3:5], 16),
                int(fallback_color[5:7], 16),
            )
        else:
            selected_color = int(fallback_color)
        logger.info(f"Using fallback color '{fallback_color}'")

    return (
        (
            SCHEMES[fallback_scheme_name](
                Hct.from_int(selected_color),
                dark_mode,
                contrast,
                spec_version=spec_version,
            )
            if selected_color
            else None
        )
        if not selected_scheme
        else selected_scheme
    )
