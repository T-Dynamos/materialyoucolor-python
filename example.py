from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_hex_from_color
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import os

from palettes.core_palette import CorePalette
from utils.theme_utils import themeFromSourceColor, getDefaultTheme, getDominantColors
from utils.color_utils import materialize
from utils.string_utils import argbFromRgb, hexFromArgb

IMAGE_FILE = "/home/tdynamos/Downloads/test.png"  # file


class Main(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("main.kv")

    def on_start(self):
        # get material dominant colors
        # (note this is in format of argb integers)
        # its count is random (maybe even 1)
        argb = getDominantColors(IMAGE_FILE, quality=100, default_chunk = 20)
        print("Generated colors ",len(argb))
        argb = argb[0]
        color = themeFromSourceColor(argb)

        self.root.ids.test.add_widget(
            MDLabel(
                text="{} Theme".format(self.theme_cls.theme_style),
                halign="center",
                bold=True,
                size_hint=(1, None),
                height=dp(60),
            )
        )

        for k in color["schemes"][self.theme_cls.theme_style.lower()].props.keys():
            label = MDLabel(text=k, halign="center", size_hint=(1, None), height=dp(60))
            widget = MDBoxLayout(size_hint=(1, None), height=dp(60))
            widget.md_bg_color = [
                k / 255
                for k in color["schemes"][self.theme_cls.theme_style.lower()].props[k]
            ] + [1]
            widget.add_widget(label)
            self.root.ids.test.add_widget(widget)

        self.root.ids.bg_.md_bg_color = hexFromArgb(argb)


Main().run()
