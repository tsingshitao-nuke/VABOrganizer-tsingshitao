import os, glob
from PIL import Image, ImageDraw

SRC = [
    r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections",
    r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP",
]
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\decode"
os.makedirs(OUT, exist_ok=True)

seen = {}
for d in SRC:
    for f in sorted(glob.glob(os.path.join(d, "*.dds"))):
        n = os.path.basename(f)
        seen.setdefault(n, f)

Z = 10          # zoom
COLS = 6
names = sorted(seen)
rows = (len(names) + COLS - 1) // COLS
CW = 32 * Z + 20
CH = 32 * Z + 34
sheet = Image.new("RGB", (COLS * CW, rows * CH), (28, 30, 36))
dr = ImageDraw.Draw(sheet)

for i, n in enumerate(names):
    im = Image.open(seen[n]).convert("RGBA")
    big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
    r, c = divmod(i, COLS)
    x, y = c * CW + 10, r * CH + 22
    # checkerboard-ish dark plate
    dr.rectangle([x - 2, y - 2, x + 32 * Z + 1, y + 32 * Z + 1], fill=(18, 20, 25), outline=(70, 76, 90))
    sheet.paste(big, (x, y), big)
    dr.text((x, y - 18), n.replace(".dds", ""), fill=(220, 225, 235))

sheet.save(os.path.join(OUT, "_sheet.png"))
print("saved", os.path.join(OUT, "_sheet.png"), sheet.size)