![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/b29c17d1-6c02-4c07-9a72-5b0198034760)

# [Material You color algorithms](https://m3.material.io/styles/color/overview) for python!

## Features 

1. Up to date with `material-foundation/material-color-utilities/`.
2. Uses official c++ sources for quantization backend, which makes color generation fast!

## Minimal running example:

Run file `tests/test_color_gen.py` as:

```console
python3 test_color_gen.py <image path> <quality>

```
Maximum quality is `1` that means use all pixels, and quality number more than `1` means how many pixels to skip in between while reading, also you can see it as compression.

<details>
    <summary>Click to view result</summary>

[Image Used, size was 8MB](https://unsplash.com/photos/zFMbpChjZGg/)

![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/9d5374c9-00b4-4b70-b82a-6792dd5c910f)
![image](https://github.com/T-Dynamos/materialyoucolor-pyhton/assets/68729523/2edd819f-8600-4c82-a18a-3b759f63a552)


</details>


## Install

You can easily install it from pip by executing:
```console
pip3 install materialyoucolor --upgrade
```
Prebuilt binaries are avaliable for `linux`, `windows` and `macos`.


## Build and install

It is built in reference with offical [typescript implementation](https://github.com/material-foundation/material-color-utilities/tree/main/typescript) but it's color quantization part is based on [c++ implementation](https://github.com/material-foundation/material-color-utilities/tree/main/cpp) thanks to [pybind](https://github.com/pybind).

```console
# Install pybind 11 
pip3 install pybind11
pip3 install https://github.com/T-Dynamos/materialyoucolor-python/archive/develop.zip

```

## FAQ
    
1. How it is different from `avanisubbiah/material-color-utilities`?

See https://github.com/T-Dynamos/materialyoucolor-python/issues/3
