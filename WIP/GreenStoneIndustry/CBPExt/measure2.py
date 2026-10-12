import os
from PIL import Image

VAN = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"
FE = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections"

TARGETS = [
    ("cs_size1  [1.25m]", os.path.join(VAN, "cs_size1.png")),
    ("cs_size2  [2.5m]", os.path.join(VAN, "cs_size2.png")),
    ("cs_size3  [3.75m]", os.path.join(VAN, "cs_size3.png")),
    ("cs_size4  [5.0m]", os.path.join(VAN, "cs_size4.png")),
    ("cs_mk2    [1.5x2.5]", os.path.join(VAN, "cs_mk2.png")),
    ("cs_mk3    [3.8x3.3]", os.path.join(VAN, "cs_mk3.png")),
    ("cs_mk4    [4.1x7.9]", os.path.join(FE, "cs_mk4.dds")),
]


def runs(im, thr=120):
    a = im.getchannel("A"); px = a.load()
    out = []
    for y in range(32):
        xs = [x for x in range(32) if px[x, y] > thr]
        if not xs:
            continue
        segs = []
        s = p = xs[0]
        for x in xs[1:]:
            if x == p + 1:
                p = x
            else:
                segs.append((s, p)); s = p = x
        segs.append((s, p))
        out.append((y, segs))
    return out


for label, path in TARGETS:
    im = Image.open(path).convert("RGBA")
    print(f"===== {label} =====")
    for y, segs in runs(im):
        txt = " ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in segs)
        print(f" y{y:>2}: {txt}")
    print()