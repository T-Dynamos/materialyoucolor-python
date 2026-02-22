/*
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "celebi.h"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <vector>

#include "wsmeans.h"
#include "wu.h"
#include "utils.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

namespace python = pybind11;

// std::map<Argb, uint32_t>
std::map<uint32_t, uint32_t> QuantizeCelebi(const std::vector<std::vector<int>>& pixels,
                               int max_colors) {
  if (max_colors > 256) {
    max_colors = 256;
  }
  int pixel_count = pixels.size();

  std::vector<material_color_utilities::Argb> opaque_pixels;
  opaque_pixels.reserve(pixel_count);
  for (int i = 0; i < pixel_count; i++) {
    uint32_t pixel = (pixels[i][0] << 16) | 
                     (pixels[i][1] << 8) | 
                     (pixels[i][2]);
    //if (pixels[i].size() > 3 && pixels[i][3] == 255) 
    opaque_pixels.push_back(pixel);
  }

  std::vector<material_color_utilities::Argb> wu_result = material_color_utilities::QuantizeWu(
      opaque_pixels, max_colors);

  material_color_utilities::QuantizerResult result =
      material_color_utilities::QuantizeWsmeans(opaque_pixels, wu_result, max_colors);
  
  return result.color_to_count;
}


std::map<uint32_t, uint32_t>  ImageQuantizeCelebi(const char* image_path, const int quality,  int max_colors) {
    int width, height, channels;
    std::vector<std::vector<int>> pixel_array = {};
    unsigned char* pixel_result = stbi_load(image_path, &width, &height, &channels, 4);
    if (!pixel_result) {return QuantizeCelebi(pixel_array, max_colors);}
    pixel_array.reserve( (width * height) / quality );
    unsigned char* pixel_position;
    int _quality = quality;
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; x = x+_quality) {
            pixel_position = pixel_result + (x + y * width) * 4;
            std::vector<int> current_color = {
              pixel_position[0], pixel_position[1], pixel_position[2]};
            if (channels > 3) {current_color.push_back(pixel_position[3]);}  
            pixel_array.push_back(current_color);
            if (_quality < quality) {_quality = quality;}
        }
        if (y % 2 == 0) {
          _quality = quality / 2;
        } else {_quality = quality;}
    }
    stbi_image_free(pixel_result);
    return QuantizeCelebi(pixel_array, max_colors);
}


PYBIND11_MODULE(celebi, m) {
    m.doc() = "Functions from cpp backend";
    m.def("QuantizeCelebi", &QuantizeCelebi, "Get dominant colors");
    m.def("ImageQuantizeCelebi", &ImageQuantizeCelebi, "Get pixel array");
}
