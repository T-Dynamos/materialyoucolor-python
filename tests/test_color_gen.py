MAX_COLOR = 128
import os
import requests
from timeit import default_timer
import sys
from materialyoucolor.utils.color_utils import rgba_from_argb
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.scheme.scheme_android import SchemeAndroid
from materialyoucolor.scheme.scheme import Scheme
from rich.console import Console
from rich.table import Table
from PIL import Image
rgba_to_hex = lambda rgba: "#{:02X}{:02X}{:02X}{:02X}".format(*map(round, rgba))

if not os.path.isfile(sys.argv[1]):
    print("Downloading test image file: ")
    with open(sys.argv[1], "wb") as file:
        file.write(
            requests.get(
        "https://unsplash.com/photos/zFMbpChjZGg/download?ixid=M3wxMjA3fDB8MXxhbGx8OHx8fHx8fDJ8fDE3MDUxMjU2NDh8&force=true").content)
    print("Downloaded!")

console = Console()

start = default_timer()
image = Image.open(sys.argv[1])

pixel_len = image.width * image.height
image_data = image.getdata()
pixel_array = [image_data[_] for _ in range(0, pixel_len, int(sys.argv[2]))]
end = default_timer()
print("File open took : ", end-start, "secs")

start = default_timer()
colors = QuantizeCelebi(pixel_array, MAX_COLOR)
selected = Score.score(colors)
end = default_timer()

print("Color generation took : ", end-start, "secs\n")


if os.name == "nt":
    # UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-5: character maps to <undefined>
    exit(0)

print("All dominant colors ({}) :\n".format(MAX_COLOR))
pused_colors = 0

for color in colors.keys():
    rgb = rgba_from_argb(color)[:-1]
    print(
        "\x1b[48;2;{};{};{}m    \x1b[0m".format(*rgb),
    end=""    
    )
    pused_colors += 1 
    if pused_colors % 16 == 0:
        print()
print()

st = Table(title = "Selected colors", title_justify = "left")
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
    schemes = [ scheme_function(rgb) for rgb in selected]
    ssct = Table(title = name, title_justify="left")
    ssct.add_column("Name")
    for rgb in selected:
        co = rgba_to_hex(rgba_from_argb(rgb))[:-2]
        ssct.add_column("[{}]██████[/{}]".format(co,co))

    for key in schemes[0].props.keys():
        __ = (key,)
        for scheme in schemes:
            color = rgba_to_hex(scheme.props[key])[:-2]
            __ += ("[{}]██████[/{}]".format(color, color),)
        ssct.add_row(*__)
    console.print(ssct)
    print()

SCHEMES = {
        Scheme.light : "Light Scheme",
        Scheme.dark : "Dark Scheme",
        SchemeAndroid.light : "Android Light Scheme",
        SchemeAndroid.dark : "Android Dark Scheme",
}

for s_f in SCHEMES.keys():
    print_scheme(s_f, SCHEMES[s_f])
