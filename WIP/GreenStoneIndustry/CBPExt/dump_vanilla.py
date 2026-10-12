import os, glob
from PIL import Image, ImageDraw

SRC = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\decode"
os.makedirs(OUT, exist_ok=True)

names = ["cs_main", "cs_size0", "cs_size1", "cs_size1p5", "cs_size2", "cs_size3",
         "cs_size4", "cs_mk2", "cs_mk3", "cs_surface"]
Z = 10
COLS = 5
rows = (len(names) + COLS - 1) // COLS
CW, CH = 32 * Z + 20, 32 * Z + 34
sheet = Image.new("RGB", (COLS * CW, rows * CH), (28, 30, 36))
dr = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    p = os.path.join(SRC, n + ".png")
    im = Image.open(p).convert("RGBA")
    big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
    r, c = divmod(i, COLS)
    x, y = c * CW + 10, r * CH + 22
    dr.rectangle([x - 2, y - 2, x + 32 * Z + 1, y + 32 * Z + 1], fill=(18, 20, 25), outline=(70, 76, 90))
    sheet.paste(big, (x, y), big)
    dr.text((x, y - 18), n, fill=(220, 225, 235))
sheet.save(os.path.join(OUT, "_vanilla_sheet.png"))
print("saved", sheet.size)

# 逐个 dump alpha + 主色
CHR = " .:-=+*#%@"
for n in ["cs_size0", "cs_size1", "cs_size2", "cs_size4", "cs_mk2", "cs_surface"]:
    im = Image.open(os.path.join(SRC, n + ".png")).convert("RGBA")
    a = im.getchannel("A"); px = a.load()
    print(f"===== {n} =====")
    for y in range(32):
        print(f"{y:>2}|" + "".join(CHR[min(9, px[x, y] * 10 // 256)] for x in range(32)) + "|")
    rgb = im.convert("RGB")
    uniq = {}
    for y in range(32):
        for x in range(32):
            if a.getpixel((x, y)) > 200:
                c = rgb.getpixel((x, y)); uniq[c] = uniq.get(c, 0) + 1
    print("主色:", sorted(uniq.items(), key=lambda kv: -kv[1])[:4])
    print()