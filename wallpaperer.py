"""wallpaperer.py

Given an image, find the background color and paste it onto a sized canvas
in some artsy way.

"""

import argparse
import sys
from math import floor

from PIL import Image

DONT_IGNORE_EDGES = False
DONT_CROP = False
SIMPLE_DETECT = False

def _center(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [floor((cwidth - iwidth) / 2), floor((cheight - iheight) / 2)]

def _center_top(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [floor((cwidth - iwidth) / 2), 0]

def _center_bottom(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [floor((cwidth - iwidth) / 2), (cheight - iheight)]

def _center_left(image_size, canvas_size)
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [0, floor((cheight - iheight) / 2)]

def _center_right(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [(cwidth - iwidth), floor((cheight - iheight) / 2)]

def _bottom_left(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [0, cheight - iheight]

def _bottom_right(image_size, canvas_size):
    iwidth, iheight = image_size
    cwidth, cheight = canvas_size
    return [cwidth - iwidth, cheight - iheight]

def _top_left(image_size, canvas_size):
    return [0, 0]

def _top_right(image_size, canvas_size):
    iwidth, _ = image_size
    cwidth, _ = canvas_size
    return [cwidth - iwidth, 0]

POSITION_VALUES = {
    "center": _center,
    "bl": _bottom_left,
    "bottom-left": _bottom_left,
    "br": _bottom_right,
    "bottom-right": _bottom_right,
    "tl": _top_left,
    "top-left": _top_left,
    "tr": _top_right,
    "top-right": _top_right,
    "center-bottom": _center_bottom,
    "center-left": _center_left,
    "center-right": _center_right,
    "center-top": _center_top,
    "cb-bottom": _center_bottom,
    "cl": _center_left,
    "cr": _center_right,
    "ct": _center_top,
}

SIZES = {
    "android-xxxhdpi": (1280, 1920),
    "android-xxhdpi": (960, 1600),
    "android-xhdpi": (640, 960),
    "android-hdpi": (480, 800),
    "android-mdpi": (320, 480),
    "android-ldpi": (240, 320),
    "hd": (1366, 768),
    "fullhd": (1920, 1080),
    "4k-uhd": (3840, 2160),
    "4k-dci": (4096, 2160)
}

def edge_pixels(img, pos="center"):
    """ Enumerate the edges of the image, top to bottom, left to right. Default
behavior is to ignore any 'hidden' edges, e.g. any edges which will be pressed
against an edge of the canvas.

    """
    width, height = img.size

    # Top edge
    if pos in ("center", "bl", "bottom-left", "br", "bottom-right") or DONT_IGNORE_EDGES:
        for windex in range(width):
            yield (windex, 0)

    # Left edge
    if pos in ("center", "bottom-right", "br", "top-right", "tr") or DONT_IGNORE_EDGES:
        for hindex in range(height):
            yield (0, hindex)

    # Right edge
    if pos in ("center", "bottom-left", "bl", "top-left", "tl") or DONT_IGNORE_EDGES:
        for hindex in range(height):
            yield (width - 1, hindex)

    # Bottom edge
    if pos in ("center", "top-right", "tr", "top-left", "tl") or DONT_IGNORE_EDGES:
        for windex in range(width):
            yield (windex, height - 1)

def flood_find(img, pos):
    """ Determine the background color of an image based on the flood fill algorithm. """

    width, height = img.size
    visited = [ [False for x in range(height) ] for x in range(width) ]
    pixels = img.load()
    areas = []

    for (ex, ey) in edge_pixels(img, pos):
        if visited[ex][ey]:
            continue

        color = pixels[ex, ey]
        pixqueue = [(ex, ey), ]
        size = 0

        while pixqueue != []:
            xx, yy = pixqueue.pop()

            # Sanity check
            if xx < 0 or xx >= width or yy < 0 or yy >= height:
                continue

            if visited[xx][yy] or pixels[xx, yy] != color:
                continue

            visited[xx][yy] = True
            size += 1

            pixqueue.append((xx + 1, yy))
            pixqueue.append((xx - 1, yy))
            pixqueue.append((xx, yy + 1))
            pixqueue.append((xx, yy - 1))

        areas.append({"color": color, "size": size})

    print(areas)
    largest_area = max(areas, key=lambda x: x["size"])
    print(largest_area)
    return largest_area["color"]

def find_background(img):
    """ Guess a background color for the image. """
    pixels = img.load()
    width, height = img.size
    colors = []

    # Top and bottom edge
    for xc in range(width):
        colors.append(pixels[xc, 0])
        colors.append(pixels[xc, height - 1])

    # Side edges
    for yc in range(height):
        colors.append(pixels[0, yc])
        colors.append(pixels[width - 1, yc])

    vote = {}
    for color in colors:
        vote[color] = vote.get(color, 0) + 1

    return max(vote)

def resize_maybe(img, canvas_size):
    """ Resize the image if it is too big. """
    width, height = img.size
    cwidth, cheight = canvas_size

    if (width > cwidth or height > cheight) or DONT_CROP:
        ratio = min(cwidth / width, cheight / height)
        scaled = (floor(width * ratio), floor(height * ratio))
        img.thumbnail(scaled)

def wallpaperer(filename, canvas_size, pos, color=None):
    """ Paste an image onto a specified canvas size. """

    # Read in the image
    img = Image.open(filename)

    # Find the background color or use the one provided
    if color is None:
        if SIMPLE_DETECT:
            color = find_background(img)
        else:
            color = flood_find(img, pos)

    # Create a canvas of proper size and color
    canvas = Image.new("RGB", size=canvas_size, color=color)

    # If the image is too big, scale it
    resize_maybe(img, canvas_size)

    # Paste onto canvas based on position
    coord = POSITION_VALUES[pos](img.size, canvas_size)
    canvas.paste(img, box=coord)

    # Save
    canvas.save("output.png")

def calculate_size(img, canvas_size, scale_oper=None):
    """ Get the new image size i the image if it is too big. """

    width, height = img.size
    cwidth, cheight = canvas_size
    new_size = img.size

    if scale_oper is None:
        # Default behavior is to scale down the image if it's too big.
        if width > cwidth or height > cheight:
            ratio = min(cwidth / width, cheight / height)
            new_size = (floor(width * ratio), floor(height * ratio))
    else:
        method, ratio = scale_oper

        if method == "scale_rel_image":
            new_size = (floor(width * ratio), floor(height * ratio))

        if method == "scale_rel_canvas":
            new_height = floor(ratio * cheight)
            ratio = new_height / height
            new_size = (floor(ratio * width), new_height)

    return new_size

def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument("filename", help="Image file to read in.")
    argparser.add_argument("position", help="Where to place the image. Values are {top-left, top-right, bottom-left, bottom-right, center}.")
    argparser.add_argument("-c", "--color", help="Color to use for the canvas.")
    argparser.add_argument("-s", "--size", help="Size to read in. This can be two numbers (width and height) separated by an 'x' or it can be one of the following: {{{0}}}.".format(", ".join(SIZES.keys())))
    argparser.add_argument("--dont-ignore", help="Default behavior ignores edges that are 'covered' by an edge of the canvas. This eliminates scenarios where the foreground runs off the edge of the original image and it's colors accidentally being picked as a background. This flag disables that behavior.", action="store_true")
    argparser.add_argument("--dont-crop", help="Default behavior is to scale images which are too big, maintaining aspect ratio. This flag disables that behavior.", action="store_true")
    argparser.add_argument("--simple", help="Use a simpler color detection. May be inaccurate but will work if your image is really big.", action="store_true")

    args = argparser.parse_args()

    DONT_CROP = args.dont_crop
    DONT_IGNORE_EDGES = args.dont_ignore
    SIMPLE_DETECT = args.simple

    if args.position not in POSITION_VALUES.keys():
        args.print_usage()
        sys.exit(1)

    if args.size is None:
        args.size = SIZES.get(args.size, (1920, 1080))
    elif 'x' in args.size:
        xc, yc = args.size.split("x")
        args.size = (int(xc), int(yc))
    else:
        argparser.print_usage()
        sys.exit(1)

    exitcode = 0
    try:
        wallpaperer(args.filename, args.size, args.position)
    except IOError as err:
        print(err)
        exitcode = -1

    sys.exit(exitcode)

if __name__ == "__main__":
    main()
