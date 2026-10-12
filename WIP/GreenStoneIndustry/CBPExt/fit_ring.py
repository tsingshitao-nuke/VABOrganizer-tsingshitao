import os, math
from PIL import Image, ImageDraw

SS, SIZE = 8, 32
W = (255, 255, 255, 255)
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\samples"
os.makedirs(OUT, exist_ok=True)


def R_for(d, sat=14.8):
    return min(sat, 7.0 + 3.0 * math.log2(d / 1.25))


def ring(path, d, sat=14.8):
    """凸齿厚度/描边随半径缩放"""
    R = R_for(d, sat)
    w = max(1.0, 0.10 * R)
    bi = min(5.0, max(1.0, 0.55 * R - 2.6))
    bo = 0.6
    half = 30.0
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = SIZE * SS / 2.0
    R, w, bi, bo = R * SS, w * SS, bi * SS, bo * SS
    po, pi = [], []
    for i in range(1441):
        a = 360.0 * i / 1440.0
        delta = min(abs(((a - n + 180) % 360) - 180) for n in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) ** 1.4 if delta < half else 0.0
        # R 是"环外径"; 无凸齿处 ri = R - w
        ro, ri = R + bo * g, R - w - bi * g
        r = math.radians(a)
        po.append((c + ro * math.cos(r), c - ro * math.sin(r)))
        pi.append((c + ri * math.cos(r), c - ri * math.sin(r)))
    dr.polygon(po + pi[::-1], fill=W)
    im.resize((SIZE, SIZE), Image.LANCZOS).save(path)


# 在与原版同半径处生成, 1:1 对照
pairs = [("cs_size1", 1.25), ("cs_size2", 2.5), ("cs_size3", 3.75)]
Z = 11
CELL = 32 * Z + 8
sheet = Image.new("RGB", (len(pairs) * CELL * 2 + 40, 32 * Z + 60), (26, 28, 34))
dr = ImageDraw.Draw(sheet)
for i, (vn, d) in enumerate(pairs):
    p = os.path.join(OUT, f"t_{vn}.png")
    ring(p, d)
    for j, src in enumerate([os.path.join(VAN, vn + ".png"), p]):
        im = Image.open(src).convert("RGBA")
        big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
        x, y = 20 + (i * 2 + j) * CELL, 40
        dr.rectangle([x, y, x + 32 * Z + 1, y + 32 * Z + 1],
                     fill=(16, 18, 22), outline=(64, 70, 84))
        sheet.paste(big, (x + 1, y + 1), big)
    dr.text((20 + i * 2 * CELL, 14), f"{vn}  {d}m   [VANILLA | NEW]",
            fill=(255, 214, 100))
sheet.save(os.path.join(OUT, "_fit.png"))
print("saved")