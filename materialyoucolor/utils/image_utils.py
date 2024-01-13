from PIL import Image
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score


def source_color_from_image(image_path: str, quality=10):
    image = Image.open(image_path)
    pixel_len = image.width * image.height
    image_data = image.getdata()
    pixel_array = [image_data[_] for _ in range(0, pixel_len, quality)]
    return Score.score(QuantizeCelebi(pixel_array, 128))[0]
