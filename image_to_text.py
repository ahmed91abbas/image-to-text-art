import sys
import cv2


def get_image_path_from_input():
    filename = None
    while not filename:
        filename = input("Enter image path:\n")
    return filename

def read_img(path):
    img_path = 'a.jpg'
    img = cv2.imread(img_path, 0)
    return img

def resize_img(img, char_width=40, char_height=None):
    scale_factor = img.shape[1] / img.shape[0]
    width = char_width
    if char_height:
        height = char_height
    else:
        height = int(char_width / scale_factor)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized

def img_to_braille(img):
    result = ""
    for row in img:
        for col in row:
            if col < 130:
                result += "#"
            else:
                result += "-"
        result += "\n"
    return result

def save_to_file(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(data)

def run(infile, outfile):
    print("Reading image file", infile)
    img = read_img(infile)
    print("Resizing image")
    print("Original image dimensions:", img.shape)
    img = resize_img(img)
    print("Resized image dimensions:", img.shape)
    print("Converting image to Braille art")
    result = img_to_braille(img)
    print("Saving to file")
    save_to_file(outfile, result)
    print("Done.")

if __name__ == '__main__':
    try:
        infile = sys.argv[1]
    except IndexError:
        infile = get_image_path_from_input()
    outfile = "output.txt"
    run(infile, outfile)