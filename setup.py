import sys

from setuptools import find_packages, setup

assert sys.version_info >= (3, 7, 0), "Materialyoucolor requires Python 3.7+"

with open("README.md", "r") as f:
    long_description = f.read()
    f.close()

with open("materialyoucolor/__init__.py","r") as file:
    VERSION = file.read().split("= ")[-1].split('"')[1].split('"')[0]
    file.close()
print(VERSION)
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
)
