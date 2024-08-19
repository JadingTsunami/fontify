from PIL import Image, ImageFont, ImageDraw, ImageColor
import os
import sys
import json

def text_to_image(
    text,
    font_filepath,
    font_size,
    color="black",
    fontmask="L",
    shadow=False,
    shadowcolor=None,
    outline=False,
    outlinecolor=None
    ):

    font = ImageFont.truetype(font_filepath, size=font_size)

    # these are "boosts" triggered by modifiers
    ascent, descent = font.getmetrics()
    width_increase = 0
    height_increase = descent

    if outline:
        width_increase += 4

    if shadow:
        width_increase += 2
        height_increase += 2

    text_width = font.getmask(text, fontmask).getbbox()[2] + width_increase
    text_height = font.getmask(text, fontmask).getbbox()[3] + height_increase
    
    img = Image.new("RGBA", (text_width, text_height))
    mask_image = font.getmask(text, fontmask)

    # shadow draws first
    if shadow:
        img.im.paste(shadowcolor, (4, 4) + (mask_image.size[0]+4,mask_image.size[1]+4), mask_image)

    if outline:
        d = ImageDraw.Draw(img)
        d.text((2, 2), text, font=font, fill=color, stroke_width=1, stroke_fill=outlinecolor, anchor='lt')
    else:
        img.im.paste(color, (0, 0) + mask_image.size, mask_image)
    return img

# Main program
data = None
with open("fontify.json", "r") as j:
    data = json.load(j)

def get(job, what, default=None):
    if what in job:
        return job[what]
    if default:
        return default
    raise TypeError(f"Error: {what} not provided and has no default.")

def process_job(job):
    # set up the path
    path = os.getcwd()
    if "path" in job:
        path = os.path.join(path, job["path"])
    else:
        path = os.path.join(path,"output")
    if not os.path.exists(path):
        os.makedirs(path)

    # assemble parameters of the job
    font = get(job, "font")
    fontsize = get(job, "fontsize")
    color = tuple(get(job, "fontcolor"))
    fontmask = get(job, "fontmask", "L")
    shadow = get(job, "shadow", False)
    shadowcolor = tuple(get(job, "shadowcolor", (int(color[0]/2), int(color[1]/2), int(color[2]/2))))
    outline = get(job, "outline", False)
    outlinecolor = tuple(get(job, "outlinecolor", (0,0,0)))

    # execute the job
    strings = get(job, "strings", None)

    if strings:
        for s in strings:
            outfile = s
            text = strings[s]
            img = text_to_image(text, font, fontsize, color, fontmask, shadow, shadowcolor, outline, outlinecolor)
            img.save(os.path.join(path, outfile + ".png"))
    else:
        # special case for STCFN*
        for n in range(33,96):
            img = text_to_image(chr(n), font, fontsize, color, fontmask, shadow, shadowcolor, outline, outlinecolor)
            img.save(os.path.join(path, f"STCFN{n:03d}.png"))

        # special case for weird/broken 121 which is actually 124 
        img = text_to_image(chr(124), font, fontsize, color, fontmask, shadow, shadowcolor, outline, outlinecolor)
        img.save(os.path.join(path, f"STCFN121.png"))

for job in data:
    process_job(job)

print("Success")
