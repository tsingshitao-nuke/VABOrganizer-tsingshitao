import os, math
from PIL import Image, ImageDraw

SS, SIZE = 8, 32
WHITE = (255, 255, 255, 255)
VAN = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
os.makedirs(OUT, exist_ok=True)


def R_for(d, sat=15.0):
    return min(sat, 7.0 + 3.0 * math.log2(d / 1.25))


def draw(d, w, bump_out, bump_in, half, path):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = SIZE * SS / 2.0
    R = R_for(d) * SS
    w, bo, bi = w * SS, bump_out * SS, bump_in * SS
    steps = 1440
    po, pi = [], []
    for i in range(steps + 1):
        a = 360.0 * i / steps
        delta = min(abs(((a - n + 180) % 360) - 180) for n in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) if delta < half else 0.0
        ro = R + w / 2 + bo * g
        ri = R - w / 2 - bi * g
        rad = math.radians(a)
        po.append((c + ro * math.cos(rad), c - ro * math.sin(rad)))
        pi.append((c + ri * math.cos(rad), c - ri * math.sin(rad)))
    dr.polygon(po + pi[::-1], fill=WHITE)
    im.resize((SIZE, SIZE), Image.LANCZOS).save(path)


# 三个候选参数, 直径 2.5m(对照原版 cs_size2)
cands = [("a", 1.6, 0.6, 2.2, 25),
         ("b", 1.4, 0.8, 2.8, 30),
         ("c", 1.2, 0.4, 3.4, 34)]
paths = {}
for tag, w, bo, bi, h in cands:
    p = os.path.join(OUT, f"c_{tag}.png")
    draw(2.5, w, bo, bi, h, p)
    paths[tag] = p

Z = 12
items = [("VANILLA cs_size2 (2.5m)", os.path.join(VAN, "cs_size2.png"))] + \
        [(f"cand {t}", paths[t]) for t, *_ in cands]
CW, CH = 32 * Z + 20, 32 * Z + 34
sheet = Image.new("RGB", (len(items) * CW, CH), (28, 30, 36))
dr = ImageDraw.Draw(sheet)
for i, (label, p) in enumerate(items):
    im = Image.open(p).convert("RGBA")
    big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
    x, y = i * CW + 10, 22
    dr.rectangle([x - 2, y - 2, x + 32 * Z + 1, y + 32 * Z + 1],
                 fill=(18, 20, 25), outline=(70, 76, 90))
    sheet.paste(big, (x, y), big)
    dr.text((x, y - 18), label, fill=(220, 225, 235))
sheet.save(os.path.join(OUT, "_cmp2.png"))
print("saved", os.path.join(OUT, "_cmp2.png"))