import os
from PIL import Image, ImageDraw

ICONS = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP\Icons"
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\samples"

groups = [
    ("VANILLA ref", [(n, VAN + "\\" + n + ".png") for n in
                     ["cs_size0", "cs_size1", "cs_size1p5", "cs_size2",
                      "cs_size3", "cs_size4", "cs_mk2", "cs_mk3"]]),
    ("NEW diameter tiers", [(n, None) for n in
                            ["cs_size0p5", "cs_size1h", "cs_size1p2", "cs_size1p8",
                             "cs_size2p5", "cs_size3p5", "cs_size4p5"]]),
    ("BORROWED", [(n, None) for n in
                  ["cs_size00", "cs_size5", "cs_size6", "cs_size7", "cs_size8",
                   "cs_mk4", "cs_proc", "cs_kpbs", "cs_hextruss", "cs_octotruss"]]),
    ("NEW big / capped", [(n, None) for n in
                          ["cs_size5p5", "cs_size6p5", "cs_size7p5", "cs_size8p8",
                           "cs_size12", "cs_size16", "cs_size24"]]),
    ("NEW Mk family (vanilla shape scaled)", [(n, None) for n in
                                              ["cs_mk0", "cs_mk3s0", "cs_mk3s1",
                                               "cs_mk3s1p5", "cs_mk3saddle",
                                               "cs_mk1p5", "cs_mk2h"]]),
    ("NEW shapes / groups", [(n, None) for n in
                             ["cs_container", "cs_vehicle", "cs_planetarybasegarage",
                              "cs_circuitboard", "cs_spinaltruss", "cs_endurance",
                              "cs_deployable", "cs_eva", "cs_strut"]]),
]

Z = 7
CELL, LABEL, COLS, PAD, TITLE_H = 32 * Z + 8, 16, 11, 12, 30
rows = []
for t, items in groups:
    rows.append(("T", t))
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
        p = path
        if not p:
            p = os.path.join(ICONS, name + ".dds")
            if not os.path.exists(p):
                p = os.path.join(ICONS, name + ".png")
        im = Image.open(p).convert("RGBA")
        big = im.resize((32 * Z, 32 * Z), Image.NEAREST)
        x = PAD + c * CELL
        dr.rectangle([x, y, x + 32 * Z + 1, y + 32 * Z + 1],
                     fill=(16, 18, 22), outline=(64, 70, 84))
        sheet.paste(big, (x + 1, y + 1), big)
        dr.text((x, y + 32 * Z + 2), name.replace("cs_", ""), fill=(200, 206, 216))
    y += CELL + LABEL

sheet.save(os.path.join(OUT, "_all_icons.png"))
print("saved", sheet.size)