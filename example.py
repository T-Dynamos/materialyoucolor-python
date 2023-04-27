import time

from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from materialyoucolor.utils.theme_utils import themeFromSourceColor, getDefaultTheme, getDominantColors, customColor 
from materialyoucolor.utils.string_utils import argbFromRgb, hexFromArgb

# Define constants
IMAGE_FILE = "/sdcard/Download/Pixel-6-Pro-Wallpaper_Hellebores-dark-by-Andrew-Zuckerman.png"  # file
THEME = "Dark"  # theme to display
COLOR_INDEX = 0  # index to build theme from

# Define Kivy Language code string for user interface
KV = """
ScrollView:
    MDBoxLayout:
        id:test
        adaptive_height:True
        orientation:"vertical"
        MDBoxLayout:
            size_hint:(1,None)
            height:60
            MDLabel:
                id:ofcolor
                text:"Colors generated: "
                halign:"center"
            MDBoxLayout:
                id:bg_
"""


class Main(MDApp):

    # Build the user interface
    def build(self):
        self.theme_cls.theme_style = THEME  # set theme style
        return Builder.load_string(KV)  # load the Kivy Language code string

    # Function to be called when the application starts
    def on_start(self):
        # Lets get color generation time
        start_time = time.time()

        # get material dominant colors
        # more default_chunk = more colors
        # less the quality number, higher the precision (max is 1) and generation time
        # you can change quality and see generation time
        argbs = getDominantColors(IMAGE_FILE, quality=10, default_chunk=128)

        # end time
        end_time = time.time()
        print("Generation time: {:.1f} secs".format(end_time - start_time))

        print("Number of Generated colors ", len(argbs))

        print("Default theme : ", getDefaultTheme()[THEME.lower()])

        # Choose a color to generate the theme from
        argb = argbs[COLOR_INDEX]  # choose index

        # add some custom colors
        # this may be needed if you have thumnail or something else like that
        # (this color will be materialized So don't worry!)
        custom_colors = [argbFromRgb(255,0,0)]

        # here argb is color int eg: 4285368085
        # generate the theme from the chosen colors
        # here custom colors will be blended from theme!
        color = themeFromSourceColor(argb, customColors=custom_colors)    

        # print custom colors!
        print("Custom color blended from theme : ", color["customColors"])

        # you can also constuct it without blending from theme color 
        print("Custom color without blending : ", customColor(custom_colors[0]))

        # Add the number of colors generated to the interface
        self.root.ids.ofcolor.text += str(len(argbs))

        # Add the theme information to the interface
        self.root.ids.test.add_widget(
            MDLabel(
                text="{} Theme from color {}".format(
                    self.theme_cls.theme_style, COLOR_INDEX + 1
                ),
                halign="center",
                bold=True,
                size_hint=(1, None),
                height=dp(60),
            )
        )

        # Iterate over the color schemes in the generated theme and add them to the interface
        for k in color["schemes"][self.theme_cls.theme_style.lower()].props.keys():
            label = MDLabel(text=k, halign="center", size_hint=(1, None), height=dp(60))
            widget = MDBoxLayout(size_hint=(1, None), height=dp(60))
            widget.md_bg_color = [
                k / 255  # convert to kivy format
                for k in color["schemes"][self.theme_cls.theme_style.lower()].props[k]
            ] + [
                1
            ]  # 1 is aplha
            widget.add_widget(label)
            self.root.ids.test.add_widget(widget)

        # Add all generated colors to layout
        for col in argbs:
            widget = MDBoxLayout()
            # Also we can convert argb to hex
            widget.md_bg_color = hexFromArgb(col)
            self.root.ids.bg_.add_widget(widget)

# run the application
Main().run()
