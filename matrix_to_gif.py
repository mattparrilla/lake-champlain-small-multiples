from images2gif import writeGif
import colorsys


def hsl_to_rgb(h, s, l):
    """Convert H, L, S color space to R, G, B"""
    normalized_color = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return tuple([int(i * 255) for i in normalized_color])


def generate_gif(images, name, directory='generated', duration=.125):
    """Creates a gif from a list of PIL images"""

    gif_name = "%s/%s.gif" % (directory, name)
    writeGif(gif_name, images, duration)
    return gif_name
