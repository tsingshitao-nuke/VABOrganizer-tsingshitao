import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iconlib import SIZE, SS, _new, _ring, _digit, _finish, R_for
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
os.makedirs(OUT, exist_ok=True)


def sample_ring(path, d, nub_half, nub_extra, w_nom):
    im, dr = _new()
    c = SIZE * SS / 2.0
    R = R_for(d) * SS
    _ring(dr, c, c, R, w_nom * SS, nub_half=nub_half, nub_extra=nub_extra)
    return _finish(im, path)


# 三个候选参数,针对 size2.5 直径(与原版 cs_size2 对比)
sample_ring(os.path.join(OUT, "s1.png"), 2.5, 22, 1.9, 2.4)
sample_ring(os.path.join(OUT, "s2.png"), 2.5, 26, 2.6, 2.0)
sample_ring(os.path.join(OUT, "s3.png"), 2.5, 30, 3.2, 1.8)

# 调色板:原版 cs_size2 作对照
VAN = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons\cs_size2.png"

Z = 10
items = [("vanilla cs_size2", Image.open(VAN).convert("RGBA"))]
for n in ["s1", "s2", "s3"]:
    items.append((n, Image.open(os.path.join(OUT, n + ".png")).convert("RGBA")))

CW, CH = 32 * Z + 20, 32 * Z + 34
sheet = Image.new("RGB", (len(items) * CW, CH), (28, 30, 36))
dr = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(items):
    big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
    x, y = i * CW + 10, 22
    dr.rectangle([x - 2, y - 2, x + 32 * Z + 1, y + 32 * Z + 1],
                 fill=(18, 20, 25), outline=(70, 76, 90))
    sheet.paste(big, (x, y), big)
    dr.text((x, y - 18), label, fill=(220, 225, 235))
sheet.save(os.path.join(OUT, "_cmp.png"))
print("saved", os.path.join(OUT, "_cmp.png"))