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

def merge_images(img1, img2):
    size1 = img1.size
    size2 = img2.size

    w = max(size1[0], size2[0])
    woffset = int(round(abs(size1[0] - size2[0])/2, 0))
    h = size1[1] + size2[1]

    img = Image.new("RGBA", (w, h))

    if w == size2[0]:
        # img2 is bigger
        img.paste(img1, (woffset,0))
        img.paste(img2, (0,size1[1]))
    else:
        # img1 is bigger
        img.paste(img1, (0,0))
        img.paste(img2, (woffset,size1[1]))

    return img

# Main program
data = None
with open("fontify.json", "r") as j:
    data = json.load(j)

def get(job, what, default="no-default"):
    if what in job:
        return job[what]
    if default != "no-default":
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
    cwilv = get(job, "cwilv", False)
    if not cwilv:
        cwilv_color = get(job, "cwilv_color", False)
        cwilv_lf = get(job, "cwilv_littlefont", False)
        cwilv_lfs = get(job, "cwilv_littlefontsize", False)
        cwilv_ol = get(job, "cwilv_outline", False)
        cwilv_olc = get(job, "cwilv_outlinecolor", False)
    else:
        cwilv_color = tuple(get(job, "cwilv_color"))
        cwilv_lf = get(job, "cwilv_littlefont")
        cwilv_lfs = get(job, "cwilv_littlefontsize")
        cwilv_ol = get(job, "cwilv_outline")
        cwilv_olc = tuple(get(job, "cwilv_outlinecolor"))

    # execute the job
    strings = get(job, "strings", None)

    if strings:
        if cwilv:
            for cw in strings:
                outfile = cw
                s0, s1 = strings[cw]
                img1 = text_to_image(s0, font, fontsize, color, fontmask, shadow, shadowcolor, outline, outlinecolor)
                img2 = text_to_image(s1, cwilv_lf, cwilv_lfs, cwilv_color, fontmask, False, False, cwilv_ol, cwilv_olc)

                img = merge_images(img1, img2)
                img.save(os.path.join(path, outfile + ".png"))
        else:
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
