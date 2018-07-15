"""wallpaperer.py

Given an image, find the background color and paste it onto a sized canvas
in some artsy way.

"""

import argparse
import sys
from math import floor

from PIL import Image

DONT_IGNORE_EDGES = False
SCALE_TO_PERCENT_HEIGHT = None
SCALE_TO_PERCENT_CANVAS_HEIGHT = None

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

def _center_left(image_size, canvas_size):
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

def edge_pixels(img, pos="center", ignore_edges=True):
    """Enumerate the edges of the image, top to bottom, left to right. Default
behavior is to ignore any 'hidden' edges, e.g. any edges which will be pressed
against an edge of the canvas.

    """
    width, height = img.size

    # Top edge
    if pos in ("center", "bl", "bottom-left", "br", "bottom-right") or (not ignore_edges):
        for windex in range(width):
            yield (windex, 0)

    # Left edge
    if pos in ("center", "bottom-right", "br", "top-right", "tr") or (not ignore_edges):
        for hindex in range(height):
            yield (0, hindex)

    # Right edge
    if pos in ("center", "bottom-left", "bl", "top-left", "tl") or (not ignore_edges):
        for hindex in range(height):
            yield (width - 1, hindex)

    # Bottom edge
    if pos in ("center", "top-right", "tr", "top-left", "tl") or (not ignore_edges):
        for windex in range(width):
            yield (windex, height - 1)


def flood_find(img, pos, ignore_edges=True):
    """ Determine the background color of an image based on the flood fill algorithm. """

    width, height = img.size
    visited = [[False for x in range(height)] for x in range(width)]
    pixels = img.load()
    areas = []

    for (ex, ey) in edge_pixels(img, pos, ignore_edges=ignore_edges):
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

    largest_area = max(areas, key=lambda x: x["size"])
    return largest_area["color"]

def find_background(img, pos="center", ignore_edges=True):
    """ Guess a background color for the image based on the pixels around the edges. """
    pixels = img.load()
    vote = {}

    for px in edge_pixels(img, pos, ignore_edges):
        xc, yc = px
        color = pixels[xc, yc]
        vote[color] = vote.get(color, 0) + 1

    return max(vote)

def wallpaperer(filename, canvas_size, pos, options):
    """ Paste an image onto a specified canvas size. """

    # Read in the image
    img = Image.open(filename)
    # Find the background color or use the one provided
    color = options.get("color", None)
    if color is None:
        if options.get("simple", False):
            color = find_background(img, pos)
        else:
            color = flood_find(img, pos, options.get("ignore_edges", True))

    # Create a canvas of proper size and color
    if len(color) == 3:
        color = (color[0], color[1], color[2], 255)
    canvas = Image.new("RGBA", size=canvas_size, color=color)

    # Rotate image if necessary
    if "rotate" in options:
        img = img.rotate(int(options["rotate"]), fillcolor=color, expand=True)

    # If the image is too big, scale it
    scale_oper = options.get("scale_oper", None)
    new_size = calculate_size(img, canvas_size, scale_oper)
    if new_size != img.size:
        img = img.resize(new_size, Image.LANCZOS)

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
    argparser.add_argument("-c", "--color", help="Color to use for the canvas. Color should be RGB or RGBA (comma-separated), or HTML hex colors.")
    argparser.add_argument("-s", "--size", help="Size to read in. This can be two numbers (width and height) separated by an 'x' or it can be one of the following: {{{0}}}.".format(", ".join(SIZES.keys())))
    argparser.add_argument("--dont-ignore-edges", help="Default behavior ignores edges that are 'covered' by an edge of the canvas. This eliminates scenarios where the foreground runs off the edge of the original image and it's colors accidentally being picked as a background. This flag disables that behavior.", action="store_false")
    argparser.add_argument("--dont-crop", help="Default behavior is to scale images which are too big, maintaining aspect ratio. This flag disables that behavior.", action="store_true")
    argparser.add_argument("--simple", help="Use a simpler color detection. May be less accurate but will work if your image is really big.", action="store_true")
    argparser.add_argument("-r", "--rotate", help="Rotate the image clockwise by the number of degrees given.")
    argparser.add_argument("--scale-rel-image", help="Scale to a percentage (written as a decimal) of the original image.")
    argparser.add_argument("--scale-rel-canvas", help="Scale to a percentage (written as a decimal) of the canvas.")

    args = argparser.parse_args()
    options = {}

    if args.position not in POSITION_VALUES.keys():
        sys.exit("wallpaperer.py: Can't place image at '{}'".format(args.position))

    for attr in ("scale_rel_canvas", "scale_rel_image", "dont_crop"):
        value = getattr(args, attr, None)
        if value:
            if "scale_oper" in options:
                sys.exit("wallpaperer.py: Can't set conflicting behaviors for cropping and resizing")
            options["scale_oper"] = (attr, float(value))

    if args.rotate is not None:
        ival = int(args.rotate)
        if ival < 0:
            sys.exit("wallpaperer.py: Cannot rotate negative degrees")
        options["rotate"] = ival

    if args.size is None:
        args.size = SIZES["fullhd"]
    elif args.size in SIZES:
        args.size = SIZES[args.size]
    elif 'x' in args.size:
        xc, yc = args.size.split("x")
        args.size = (int(xc), int(yc))
    else:
        sys.exit("wallpaperer.py: Must provide a proper canvas size")

    if args.color is not None:
        if "," in args.color:
            args.color = tuple(int(x) for x in args.color.split(","))
        options["color"] = args.color

    options["simple"] = args.simple
    options["ignore_edges"] = (not args.dont_ignore_edges)

    exitcode = 0
    try:
        wallpaperer(args.filename, args.size, args.position, options)
    except IOError as err:
        print(err)
        exitcode = -1

    sys.exit(exitcode)

if __name__ == "__main__":
    main()
