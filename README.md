# img2ascii

This is a simple tool that I made in an afternoon to take image files as input and turn them into text files containing images constructed out of text characters. 

# Usage

There are several command line options available, delineated below. Arguments are surrounded by `<>` for purpose of demonstration; these should be omitted when running. 

 - `in=<path/to/image.png>`: specify the image path; defaults to `in.jpg`.
 - `out=<path/to/text.txt>`: specify the text output path - if not specified, the program will print the output without exporting; if specified, the program will export the output without printing.
 - `lut=<path/to/lut.json>`: specify the look-up table JSON file, if you have your own; defaults to `lut.json`, which comes pre-populated.
 - `font=<path/to/font.bdf>`: specify your BDF font file; defaults to `font.bdf`.
 - `charset="<abcdefghi...>"`: specify a literal set of characters to use as your character set.
 - `charset=<charset_name>`: specify the name of a character set defined in `charsets.json`; defaults to `ascii`, but other options are `blocks`, `box_drawing`, and `shapes`.
 - `dims=<123>,<123>`: specify the dimensions as `width,height` of the output file; defaults to `128,128`. Do not include a space after the comma.
 - `w=<123>`: specify the width of the output file; defaults to `128`.
 - `h=<123>`: specify the height of the output file; defaults to `128`.

In the case of duplicative agruments, options that occur later in the sequence are given precedence.

## Examples

```sh
python3 img2ascii.py in=pickles.png out=pickles.txt charset="0123456789"
```

will convert the image `pickles.png` to a text image using only the characters in the set "0123456789". The resulting text file will contain 128 lines that are 128 characters wide each.

```sh
python3 img2ascii.py dims=400,400 w=60
```

This will convert the image `in.jpg` to a text image using the ASCII character set and will produce an output that is 400 lines long, each line of which is 60 characters wide. 

# Methodology

## Character lightness

Firstly, I wanted a way to compare how "dark" or "light" characters in a character set (i.e. ASCII) are. For example, "M" is always going to be a much "darker" character than "." because it uses more pixels for the same amount of space.

To quantify lightness/darkness of an individual character, I wrote a section of the program to take one character, produce a grayscale image file containing a glyph of only this one character, then average the lightness values of each pixel in the image. When repeated for a whole character set, we get an easy way to compare which characters occupy more pixels than others. 

The first way that I could find to implement this in Python without using heavy-weight software like FontForge was to use an older font format called (Glyph) BDF, or [Glyph Bitmap Distribution Format](https://en.wikipedia.org/wiki/Glyph_Bitmap_Distribution_Format), along with a Python library called `bdfparser` that works with the Python Imaging Library (PIL) to easily allow developers to create image files constructed from text characters. Thanks to PIL's functionality, it is straightforward to average pixel lightness values from here onward and to do so for every character in a set. To avoid having to re-compute lightness values for every character at runtime, I have the lightness values stored in a look-up table as `lut.json` that is continually updated as character sets change. In the future, I would like to extend this file to contain look-up tables for multiple character sets.

The font you choose probably does not matter all that much, as long as it is in BDF format. Here is a list of 57 fonts in BDF format, some of which are public domain: https://ha1tch.github.io/bdf-fonts/font_catalogue.html

## Character Sets

You can really choose any set of Unicode characters that your shell will display. I have provided the ASCII characters, Unicode's block characters, box-drawing characters, and geometric shape characters as examples. 

## Mapping Pixels to Characters

Upon examining the look-up table for the ASCII character set, we see that the darkest character ("M") has a lightness value of only ≈168, while the minimum lightness value is 0. Additionally, there are far fewer characters in a character set than there are possible lightness values. To rectify this, the program re-aligns the character set such that the darkest character maps to the value of the darkest pixel in the provided image and the lightest character maps to the value of the lightest pixel in the provided image, and the remaining characters are evenly-spaced throughout the lightness range. As long as the characters are sorted by lightness, the actual lightness values do not matter that much (until we start thinking about image contrast). Then, to map pixel value to a character, one need only search for the character whose newly aligned lightness value is closest to the lightness value of the piexl. 

# Dependencies

This project uses:
 - `PIL` for image processing
 - `numpy` for array math
 - `bdfparser` for generating images of glyphs in BDF font files (https://pypi.org/project/bdfparser/)
 - `json` and `sys` for handling files and command line arguments

# Issues

1. Sometimes the images come out rotated. I do not know why. 
