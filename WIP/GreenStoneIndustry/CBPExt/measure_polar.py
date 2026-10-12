import os, math
from PIL import Image

VAN = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\Squad\PartList\SimpleIcons"


def polar(im, name):
    a = im.getchannel("A"); px = a.load()
    c = 15.5
    print(f"--- {name} : 每 5 度, 外径R / 厚度 ---")
    line = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        dx, dy = math.cos(rad), -math.sin(rad)
        on = []
        r = 0.0
        while r < 16:
            x, y = int(round(c + dx * r)), int(round(c + dy * r))
            if 0 <= x < 32 and 0 <= y < 32 and px[x, y] > 60:
                on.append(r)
            r += 0.2
        out = max(on) if on else 0
        # thickness at this angle
        th = 0.0
        if on:
            seg = 1; best = 1; prev = on[0]
            for v in on[1:]:
                if v - prev < 0.5:
                    seg += 1
                else:
                    best = max(best, seg); seg = 1
                prev = v
            th = best * 0.2
        line.append(f"{deg:>3}:R{out:>4.1f}/t{th:>3.1f}")
    for i in range(0, len(line), 6):
        print("   " + "  ".join(line[i:i + 6]))


for n in ["cs_size1", "cs_size2", "cs_size3"]:
    polar(Image.open(os.path.join(VAN, n + ".png")).convert("RGBA"), n)