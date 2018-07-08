# wallpaperer

Turn simple images and fan art with solid-color backgrounds into desktop
wallpapers. Unfortunately such a simple script is only possible with images that
have solid color backgrounds that touch the edges. Think vector art and fanart.

```
usage: wallpaperer.py [-h] [-c COLOR] [-s SIZE] [--dont-ignore] [--dont-crop]
                      [--simple] [-r ROTATE]
                      [--scale-rel-image SCALE_REL_IMAGE]
                      [--scale-rel-canvas SCALE_REL_CANVAS]
                      filename position

positional arguments:
  filename              Image file to read in.
  position              Where to place the image. Values are {top-left, top-
                        right, bottom-left, bottom-right, center}.

optional arguments:
  -h, --help            show this help message and exit
  -c COLOR, --color COLOR
                        Color to use for the canvas.
  -s SIZE, --size SIZE  Size to read in. This can be two numbers (width and
                        height) separated by an 'x' or it can be one of the
                        following: {android-xxxhdpi, android-xxhdpi, android-
                        xhdpi, android-hdpi, android-mdpi, android-ldpi, hd,
                        fullhd, 4k-uhd, 4k-dci}.
  --dont-ignore         Default behavior ignores edges that are 'covered' by
                        an edge of the canvas. This eliminates scenarios where
                        the foreground runs off the edge of the original image
                        and it's colors accidentally being picked as a
                        background. This flag disables that behavior.
  --dont-crop           Default behavior is to scale images which are too big,
                        maintaining aspect ratio. This flag disables that
                        behavior.
  --simple              Use a simpler color detection. May be less accurate
                        but will work if your image is really big.
  -r ROTATE, --rotate ROTATE
                        Rotate the image clockwise by the number of degrees
                        given.
  --scale-rel-image SCALE_REL_IMAGE
                        Scale to a percentage (written as a decimal) of the
                        original image.
  --scale-rel-canvas SCALE_REL_CANVAS
                        Scale to a percentage (written as a decimal) of the
                        canvas.
```

A word of advice, though: the tool is really simple. If you've tried more than
three different settings and it still doesn't look good with your image, you
probably need to just open up PS and do it yourself.

## Example

Here's a nice picture of Madotsuki, from the classic game Yume Nikki:

![Madotsuki](https://github.com/dwwmmn/wallpaperer/blob/master/example/madotsuki.jpg)

(Note: I looked around for copyright of this image and couldn't find it. It's
all over the Internet so I figured it was safe. If you own it and are mad that I
rehost Please Don't Sue Me, just send me an email.)

Using the following command, we can easily turn it into a wallpaper which fits
your average HD screen:

```bash
python wallpaperer.py --size 1920x1080 madotsuki.jpg bottom-left
```

![Madotsuki wallpaper](https://github.com/dwwmmn/wallpaperer/blob/master/example/madotsuki-wallpaper.png)

Ta-da! Note how wallpaperer detects the background color and extends it to fit
the whole screen.