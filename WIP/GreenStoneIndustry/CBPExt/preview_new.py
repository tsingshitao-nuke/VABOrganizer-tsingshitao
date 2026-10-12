import os
from PIL import Image, ImageDraw

ICONS = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP\Icons"
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\samples"

groups = [
    ("VANILLA (KSP built-in, size0..4)", [
        ("cs_size0", VAN + r"\cs_size0.png"),
        ("cs_size1", VAN + r"\cs_size1.png"),
        ("cs_size1p5", VAN + r"\cs_size1p5.png"),
        ("cs_size2", VAN + r"\cs_size2.png"),
        ("cs_size3", VAN + r"\cs_size3.png"),
        ("cs_size4", VAN + r"\cs_size4.png")]),
    ("NEW diameter tiers", [
        ("cs_size0p5", None), ("cs_size1p2", None), ("cs_size1p8", None),
        ("cs_size2p5", None), ("cs_size3p5", None), ("cs_size4p5", None)]),
    ("BORROWED (your 7 + FE 3)", [
        ("cs_size00", None), ("cs_size5", None), ("cs_size6", None),
        ("cs_size7", None), ("cs_size8", None), ("cs_kpbs", None),
        ("cs_mk4", None), ("cs_proc", None), ("cs_hextruss", None),
        ("cs_octotruss", None)]),
    ("NEW big-with-digit", [
        ("cs_size5p5", None), ("cs_size6p5", None), ("cs_size7p5", None)]),
    ("NEW shapes", [
        ("cs_mk0", None), ("cs_mk1p5", None), ("cs_mk2h", None),
        ("cs_mk3s0", None), ("cs_mk3s1", None), ("cs_mk3s1p5", None),
        ("cs_container", None), ("cs_vehicle", None), ("cs_spinaltruss", None)]),
]

Z = 7
CELL = 32 * Z + 8
LABEL = 16
COLS = 10
PAD = 12
TITLE_H = 30

rows = []
for title, items in groups:
    rows.append(("T", title))
    for i in range(0, len(items), COLS):
        rows.append(("I", items[i:i + COLS]))

W = PAD * 2 + COLS * CELL
H = PAD * 2 + sum(TITLE_H if k == "T" else CELL + LABEL for k, _ in rows)
sheet = Image.new("RGB", (W, H), (26, 28, 34))
dr = ImageDraw.Draw(sheet)

y = PAD
for kind, val in rows:
    if kind == "T":
        dr.text((PAD, y + 8), val, fill=(255, 214, 100))
        y += TITLE_H
        continue
    for c, (name, path) in enumerate(val):
        p = path or os.path.join(ICONS, name + ".dds")
        if not path and not os.path.exists(p):
            p = os.path.join(ICONS, name + ".png")
        im = Image.open(p).convert("RGBA")
        big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
        x = PAD + c * CELL
        dr.rectangle([x, y, x + 32 * Z + 1, y + 32 * Z + 1],
                     fill=(16, 18, 22), outline=(64, 70, 84))
        sheet.paste(big, (x + 1, y + 1), big)
        dr.text((x, y + 32 * Z + 2), name.replace("cs_", ""), fill=(200, 206, 216))
    y += CELL + LABEL

sheet.save(os.path.join(OUT, "_new_icons.png"))
print("saved", sheet.size)