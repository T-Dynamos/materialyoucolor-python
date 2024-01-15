import os
import sys
import urllib.request
from glob import glob
from setuptools import find_packages, setup
from setup_helpers import Pybind11Extension

assert sys.version_info >= (3, 7, 0), "Materialyoucolor requires Python 3.7+"

with open("README.md", "r") as f:
    long_description = f.read()
    f.close()

with open("materialyoucolor/__init__.py", "r") as file:
    VERSION = file.read().split("= ")[-1].split('"')[1].split('"')[0]
    file.close()

def get_extension():
    FOLDER = "./materialyoucolor/quantize/"
    PATCH_FILE = "quantizer_cpp.patch"
    COMMIT = "1217346b9416e6e55c83c6e9295f6aed001e852e"
    URL = (
        "https://raw.githubusercontent.com/material-foundation/"
        "material-color-utilities/{}/cpp/".format(COMMIT)
    )
    FILES = list(
        "quantize/" + __
        for __ in [
            "wu.h",
            "wu.cc",
            "wsmeans.h",
            "wsmeans.cc",
            "lab.h",
            "lab.cc",
            "celebi.h",
            "celebi.cc",
        ]
    ) + ["utils/utils.h", "utils/utils.cc"]
        
    if all([os.path.isfile(os.path.join(FOLDER, os.path.basename(_))) for _ in FILES]):
        print("Skipping download...")
    else:
        print("Downloading required files...")
        for file in FILES:
            with open(os.path.join(FOLDER, os.path.basename(file)), "w") as write_buffer:
                write_buffer.write(urllib.request.urlopen(URL + file).read().decode("utf-8"))
                write_buffer.close()
                print("[Downloaded] : " + file)

        print("Applying patch : ", PATCH_FILE)
        if os.system("patch --directory={} --strip=1 < {}".format(FOLDER, PATCH_FILE)) == 0:
            print("Applied Successfully...")
        else:
            print("Failed!") 

    return Pybind11Extension(
        "materialyoucolor.quantize.celebi",
        sorted(glob("materialyoucolor/quantize/*.cc")),
        extra_compile_args=['-std=c++17'] if os.name != 'nt' else ['/std:c++17']
        )


setup(
    name="materialyoucolor",
    version=VERSION,
    description="Material You color generation algorithms in pure python!",
    author="Ansh Dadwal",
    author_email="anshdadwal298@gmail.com",
    packages=find_packages(),
    install_requires=["pillow"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    exclude=["README.md", "*.pyc", "example.py"],
    ext_modules=[get_extension()]
)
