from bdfparser import Font
from PIL import Image
import numpy as np
import json
import sys


LUT_PATH = "lut.json"
IMG_PATH = "in.jpg"
OUT_PATH = ""
FONT_BDF_PATH = "font.bdf"
DEFAULT_CHARSET = "ascii"
DIMS = (128, 128)

with open("charsets.json", "r") as f:
    charsets = json.load(f)
    f.close()

CHARS = charsets[DEFAULT_CHARSET]


def make_lut(fontfile: str, chars: str | list) -> dict:
    lut = {}

    for char in chars:
        font = Font(fontfile)
        text = font.glyph(char).draw()

        img = Image.frombytes('L', (text.width(), text.height()), text.tobytes('L'))
        imgarray = np.asarray(img)

        lut.update({char: float(imgarray.mean())})

    sorted_lut = {}

    for letter in sorted(lut, key=lut.get):
        sorted_lut.update({letter: lut[letter]})
    
    return sorted_lut


def convert_image(lut: dict[str, float], dims: tuple[int, int], image_path: str) -> str:
    chars = sorted(lut, key=lut.get)

    img = Image.open(image_path).convert("L")
    img = img.resize(dims)
    imgarray = np.asarray(img)

    grayscale_range = np.linspace(
        imgarray.min(),
        imgarray.max(),
        len(chars)
    )

    new_lut = {}

    for i in range(len(chars)):
        new_lut.update({chars[i]: 255 - grayscale_range[i]})


    def find_closest_char(grayscale_val: int):
        min_dist_char = ''
        min_dist = 256
        
        for char in chars:
            dist = abs(new_lut[char] - grayscale_val)
            if dist < min_dist:
                min_dist = dist
                min_dist_char = char
        return min_dist_char


    textarray = [[" " for _ in range(img.width)] for __ in range(img.height)]

    for i, row in enumerate(imgarray):
        for j, val in enumerate(row):
            textarray[i][j] = find_closest_char(val)

    return "\n".join(["".join(row) for row in textarray])


def check_reload_lut(lut: dict[str, float], chars: str | list):
    return sorted(list(lut.keys())) != sorted(list(chars))


def convert(lut_path: str, chars: str | list, dims: tuple[int, int], image_path: str, fontfile: str, output_path: str = ""):
    with open(lut_path, "r") as f:
        lut = json.load(f)
        f.close()
    
    if check_reload_lut(lut, chars):
        lut = make_lut(fontfile, chars)

        with open(lut_path, "w") as f:
            f.write(json.dumps(lut, indent=2))
            f.close()
    
    output = convert_image(lut, dims=dims, image_path=image_path)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
            f.close()
    else:
        print(output)



if __name__ == "__main__":
    for arg in sys.argv:
        if arg.startswith("in="):
            IMG_PATH = arg.replace("in=", "")
        elif arg.startswith("out="):
            OUT_PATH = arg.replace("out=", "")
        elif arg.startswith("lut="):
            LUT_PATH = arg.replace("lut=", "")
        elif arg.startswith("font="):
            FONT_BDF_PATH = arg.replace("font=", "")
        elif arg.startswith("dims="):
            txttuple = arg.replace("dims=", "")
            txttuple = txttuple.split(",")
            DIMS = (int(txttuple[0]), int(txttuple[1]))
        elif arg.startswith("w="):
            DIMS = (int(arg.replace("w=", "")), DIMS[1])
        elif arg.startswith("h="):
            DIMS = (DIMS[0], int(arg.replace("h=", "")))
        elif arg.startswith("charset=\""):
            CHARS = arg.replace("\"", "").replace("charset=", "")
        elif arg.startswith("charset=") and not arg.startswith("charset=\""):
            DEFAULT_CHARSET = arg.replace("charset=", "")
            CHARS = charsets[DEFAULT_CHARSET]
    
    convert(lut_path=LUT_PATH, dims=DIMS, chars=CHARS, image_path=IMG_PATH, fontfile=FONT_BDF_PATH, output_path=OUT_PATH)