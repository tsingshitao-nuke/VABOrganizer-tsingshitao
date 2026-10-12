import os
from PIL import Image

SRC = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"
FE = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections"

# vanilla diameter table (FilterExtensions labels + KSP wiki)
VAN = [("cs_size0", 0.625), ("cs_size1", 1.25), ("cs_size1p5", 1.875),
       ("cs_size2", 2.5), ("cs_size3", 3.75), ("cs_size4", 5.0)]


def outer_radius(im, cx=15.5, cy=15.5):
    """max distance from centre where alpha>0, measured along the 0/90 deg axes
    (avoiding the diagonal bumps) -> gives the ring outer radius"""
    a = im.getchannel("A")
    px = a.load()
    best = 0.0
    for y in range(32):
        for x in range(32):
            if px[x, y] > 8:
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                best = max(best, d)
    return best


def ring_bbox(im):
    a = im.getchannel("A")
    bb = a.getbbox()
    return bb


print(f"{'file':<16}{'diam(m)':>9}{'bbox':>22}{'bbox_w':>8}{'maxR':>7}")
print("-" * 66)
data = []
for n, d in VAN:
    im = Image.open(os.path.join(SRC, n + ".png")).convert("RGBA")
    bb = ring_bbox(im)
    w = bb[2] - bb[0]
    R = outer_radius(im)
    data.append((d, w, R))
    print(f"{n:<16}{d:>9}{str(bb):>22}{w:>8}{R:>7.2f}")

print()
# also measure the FE big ones for reference
FE_TAB = [("cs_size00", 0.3125), ("cs_size5", 6.25), ("cs_size6", 7.5),
          ("cs_size7", 8.75), ("cs_size8", 10.0)]
for n, d in FE_TAB:
    p = os.path.join(FE, n + ".dds")
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGBA")
    bb = ring_bbox(im)
    w = bb[2] - bb[0]
    R = outer_radius(im)
    print(f"{n:<16}{d:>9}{str(bb):>22}{w:>8}{R:>7.2f}")

print()
print("=== 拟合: 直径 -> 结构宽度(bbox_w) ===")
for d, w, R in data:
    print(f"  {d:>6.3f}m -> w={w:>2}px   比值 px/m = {w/d:.3f}")
import statistics
ratios = [w / d for d, w, R in data]
print("  比值均值:", round(statistics.mean(ratios), 3), " 中位:", round(statistics.median(ratios), 3))