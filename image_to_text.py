import sys
import cv2
import json
import numpy as np
import math
import requests
import re


def read_json(filename):
    with open(filename, "r", encoding="utf8") as infile:
        return json.load(infile)

def pad_image(img, padding_value=255):
    nbr_col_paddings = 2 * math.ceil(len(img[0]) / 2) - len(img[0])
    nbr_row_paddings = 4 * math.ceil(len(img) / 4) - len(img)

    pad_rows = np.array([[padding_value] * len(img[0])] * nbr_row_paddings)
    if len(pad_rows):
        img = np.concatenate((img, pad_rows), axis=0)

    pad_cols = np.full((len(img), nbr_col_paddings), padding_value)
    if len(pad_cols):
        img = np.append(img, pad_cols, axis=1)

    return img

def get_image_path_from_input():
    filename = None
    while not filename:
        filename = input("Enter image path:\n")
    return filename

def read_img_data(indata):
    if re.match('(https?://[0-9A-Za-z-._~?/#]+)', indata):
        return read_img_from_url(indata)
    else:
        return read_img(indata)

def read_img(path):
    img = cv2.imread(path, 0)
    return img

def read_img_from_url(url):
    req = requests.get(url)
    arr = np.asarray(bytearray(req.content), dtype=np.uint8)
    return cv2.imdecode(arr, 0)

def resize_img(img, char_width=80, char_height=None):
    scale_factor = img.shape[1] / img.shape[0]
    width = char_width
    if char_height:
        height = char_height
    else:
        height = int(char_width / scale_factor)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized

def get_braille_value(matrix, mapping, blank_value):
    ''' Dot numering following the ISO/TR 11548-1
    standard for 8-dot Braille
    1 4
    2 5
    3 6
    7 8'''
    key = ""
    if matrix[0][0] < blank_value:
        key += "1"
    if matrix[1][0] < blank_value:
        key += "2"
    if matrix[2][0] < blank_value:
        key += "3"
    if matrix[0][1] < blank_value:
        key += "4"
    if matrix[1][1] < blank_value:
        key += "5"
    if matrix[2][1] < blank_value:
        key += "6"
    if matrix[3][0] < blank_value:
        key += "7"
    if matrix[3][1] < blank_value:
        key += "8"

    if key:
        return mapping[key]

    return mapping["BLANK"]

def blockshaped(arr, nrows, ncols):
    # Source https://stackoverflow.com/a/16858283
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

def img_to_braille(img, mapping, blank_value):
    result = ""
    count = 0
    for matrix in blockshaped(img, 4, 2):
        result += get_braille_value(matrix, mapping, blank_value)
        count += 1
        if count == len(img[0]) / 2:
            count = 0
            result += "\n"
    return result

def save_to_file(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(data)

def run(indata, outfile, mapping, resize_width, blank_value):
    print("Reading image data", indata)
    img = read_img_data(indata)

    print("Resizing image")
    print("Original image dimensions:", img.shape)
    img = resize_img(img, char_width=resize_width)
    print("Resized image dimensions:", img.shape)

    print("Padding image")
    img = pad_image(img)
    print("Final image dimensions:", img.shape)

    print("Converting image to Braille art")
    result = img_to_braille(img, mapping, blank_value)

    print("Saving to file")
    save_to_file(outfile, result)

    print("Done.")


if __name__ == '__main__':
    mapping = read_json("binary_braille_mappings.json")
    resize_width = 74
    blank_value = 200
    try:
        indata = sys.argv[1]
    except IndexError:
        indata = get_image_path_from_input()
    outfile = "output.txt"
    run(indata, outfile, mapping, resize_width, blank_value)
