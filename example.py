import time

from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from utils.theme_utils import themeFromSourceColor, getDefaultTheme, getDominantColors
from utils.string_utils import argbFromRgb, hexFromArgb

IMAGE_FILE = "/home/tdynamos/Downloads/test.png"  # file
THEME = "Dark" # theme to display

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
                text:"Color from image :"
                halign:"center"
            MDBoxLayout:
                id:bg_
"""

class Main(MDApp):

    def build(self):
        self.theme_cls.theme_style = THEME
        return Builder.load_string(KV)

    def on_start(self): 
        # Lets get color generation time 
        start_time = time.time()

        # get material dominant colors
        # more default_chunk = more colors
        # less the quality number, higher the precision (max is 1) and generation time 
        # you can change quality and see generation time 
        argbs = getDominantColors(IMAGE_FILE, quality=10, default_chunk = 128)
        
        # end time 
        end_time = time.time()
        print("Generation time: {:.1f} secs".format(end_time - start_time))

        print("Number of Generated colors ",len(argbs))

        print("Default theme (without color): ",getDefaultTheme())

        argb = argbs[0] # choose index 0

        # here argb is color int eg: 4285368085
        color = themeFromSourceColor(argb) # generate theme from color 

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
                k / 255 # kivy does it 
                for k in color["schemes"][self.theme_cls.theme_style.lower()].props[k]
            ] + [1] # 1 is aplha 
            widget.add_widget(label)
            self.root.ids.test.add_widget(widget)

        self.root.ids.bg_.md_bg_color = hexFromArgb(argb)


Main().run()
