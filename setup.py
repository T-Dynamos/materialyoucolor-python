import os
import re
import sys
from glob import glob
from pathlib import Path

from setuptools import find_packages, setup

OPTIONS = ["PURE_PYTHON"]

for option in OPTIONS:
    globals()[option] = False
    option_name = "--" + option.lower().replace("_", "-")
    if option_name in sys.argv or "MYCP_" + option in os.environ:
        while option_name in sys.argv:
            sys.argv.remove(option_name)
        globals()[option] = True

assert sys.version_info >= (3, 7, 0), "Materialyoucolor requires Python 3.7+"


BASE_DIR = Path(__file__).parent
LONG_DESCRIPTION = (BASE_DIR / "README.md").read_text(encoding="utf-8")
VERSION_FILE = (BASE_DIR / "materialyoucolor" / "__init__.py").read_text(
    encoding="utf-8"
)
VERSION = re.search(r'__version__\s*=\s*"([^"]+)"', VERSION_FILE).group(1)


ext_modules = []
cmdclass = {}
if not PURE_PYTHON:
    from pybind11.setup_helpers import Pybind11Extension, build_ext

    ext_modules = [
        Pybind11Extension(
            "materialyoucolor.quantize.celebi",
            sorted(glob("materialyoucolor/quantize/*.cc")),
            cxx_std=17,
        )
    ]
    cmdclass = {"build_ext": build_ext}


setup(
    name="materialyoucolor",
    version=VERSION,
    description="Material You color generation algorithms in pure python!",
    author="Ansh Dadwal",
    author_email="anshdadwal298@gmail.com",
    packages=find_packages(),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=[
        "pillow",
    ],
    ext_modules=ext_modules,
    cmdclass=cmdclass,
)
