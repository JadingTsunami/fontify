# Image Font Generator

Requires pillow, json

Create menu, status bar, and message font image replacements.

Program will read `fontify.json` and process each job inside.

Jobs can have these fields:

* `strings` (optional): Dictionary. Keys are the filename. Value is the string.
    - If not present, will produce a "message font" (`STCFNxxx`)
* `font` (required): Path to a TrueType font to use.
* `fontsize` (required): Size of the font to generate for this job.
* `fontcolor` (required): RGB color. You can use any RGB color picker like [this one](https://rgbcolorpicker.com/) to get the numbers to use.
* `fontmask` (optional): Put "L" to get aliased font (blurry edges). For hard edges, use "1".
* `path` (optional): What subfolder of the current working directory to place the files from this job. If not supplied, a folder named "output" will be used.
* `shadow` (optional): true/false - whether or not to put a drop shadow below the text.
* `shadowcolor` (optional): If supplied, the drop shadow color. Else half the primary text color is used.
* `outline` (optional): true/false - whether or not to outline the text with a thin line.
* `outlinecolor`: If supplied, the outline color. Else black.

