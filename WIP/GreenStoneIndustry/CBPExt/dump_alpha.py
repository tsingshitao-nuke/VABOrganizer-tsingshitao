import os, glob
from PIL import Image

SRC = [
    r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections",
    r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP",
]
seen = {}
for d in SRC:
    for f in sorted(glob.glob(os.path.join(d, "*.dds"))):
        seen.setdefault(os.path.basename(f), f)

CH = " .:-=+*#%@"


def dump(name):
    im = Image.open(seen[name + ".dds"]).convert("RGBA")
    a = im.getchannel("A")
    px = a.load()
    print(f"===== {name} =====")
    for y in range(32):
        line = "".join(CH[min(9, px[x, y] * 10 // 256)] for x in range(32))
        print(f"{y:>2}|{line}|")
    # color of opaque pixels
    rgb = im.convert("RGB")
    opaque = [(rgb.getpixel((x, y)), a.getpixel((x, y)))
              for y in range(32) for x in range(32) if a.getpixel((x, y)) > 200]
    if opaque:
        uniq = {}
        for c, _ in opaque:
            uniq[c] = uniq.get(c, 0) + 1
        top = sorted(uniq.items(), key=lambda kv: -kv[1])[:4]
        print("主色:", top)
    print()


for n in ["cs_size5", "cs_size7", "cs_kpbs", "cs_size00", "cs_mk4", "cs_octotruss", "cs_proc"]:
    dump(n)