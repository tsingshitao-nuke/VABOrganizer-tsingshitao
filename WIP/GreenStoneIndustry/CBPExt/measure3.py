import os, math
from PIL import Image

VAN = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"
FE = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections"

CX = CY = 15.5
THR = 60


def ray(im, deg):
    """outermost radius (and stroke thickness) along a ray, alpha>THR"""
    a = im.getchannel("A"); px = a.load()
    rad = math.radians(deg)
    dx, dy = math.cos(rad), -math.sin(rad)
    hits = []
    r = 0.0
    while r < 16:
        x = int(round(CX + dx * r)); y = int(round(CY + dy * r))
        if 0 <= x < 32 and 0 <= y < 32:
            hits.append((r, px[x, y]))
        r += 0.25
    on = [r for r, v in hits if v > THR]
    if not on:
        return 0.0, 0.0, 0.0
    outer = max(on)
    # thickness = longest contiguous run
    best = 0.0; s = None; prev = None
    for r, v in hits:
        if v > THR:
            if s is None:
                s = r
            prev = r
        else:
            if s is not None:
                best = max(best, prev - s); s = None
    if s is not None:
        best = max(best, prev - s)
    return outer, best, min(on)


VAN_TAB = [("cs_size0", 0.625), ("cs_size1", 1.25), ("cs_size1p5", 1.875),
           ("cs_size2", 2.5), ("cs_size3", 3.75), ("cs_size4", 5.0)]
FE_TAB = [("cs_size00", 0.3125), ("cs_size5", 6.25), ("cs_size6", 7.5),
          ("cs_size7", 8.75), ("cs_size8", 10.0)]

print(f"{'icon':<12}{'diam':>7}{'R@0deg':>9}{'R@45deg':>9}{'R@90':>7}{'strok45':>9}{'strok90':>9}")
print("-" * 62)
rows = []
for n, d in VAN_TAB:
    im = Image.open(os.path.join(VAN, n + ".png")).convert("RGBA")
    r0, s0, _ = ray(im, 0)
    r45, s45, _ = ray(im, 45)
    r90, s90, _ = ray(im, 90)
    rows.append((d, r0, r45, s45))
    print(f"{n:<12}{d:>7}{r0:>9.2f}{r45:>9.2f}{r90:>7.2f}{s45:>9.2f}{s90:>9.2f}")

print()
for n, d in FE_TAB:
    p = os.path.join(FE, n + ".dds")
    if not os.path.exists(p): continue
    im = Image.open(p).convert("RGBA")
    r0, s0, _ = ray(im, 0)
    r45, s45, _ = ray(im, 45)
    r90, s90, _ = ray(im, 90)
    print(f"{n:<12}{d:>7}{r0:>9.2f}{r45:>9.2f}{r90:>7.2f}{s45:>9.2f}{s90:>9.2f}")

print()
print("=== 拟合 R_ring(45deg) 与直径 ===")
for d, r0, r45, s45 in rows:
    print(f"  d={d:<6} R45={r45:.2f}  R45/d={r45/d:.3f}  R45/sqrt(d)={r45/math.sqrt(d):.3f}")