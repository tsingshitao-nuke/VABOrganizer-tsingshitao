"""生成 CBP 图标(新造 18 张)。风格复刻 KSP 原版 Squad/PartList/SimpleIcons:
  纯白 255 透明底, 32x32, 轮廓 + 四向(0/90/180/270)凸齿。
  R 定义为"环外径", 与原版实测一致。
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

SS, SIZE = 8, 32
W = (255, 255, 255, 255)
CB = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP"
ICONS = os.path.join(CB, "Icons")
FONTS = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]


def font(px):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            pass
    return ImageFont.load_default()


def dR(d, sat=14.8):
    """直径(m) -> 环外径(px)"""
    return min(sat, 7.0 + 3.0 * math.log2(d / 1.25))


def _shape(a, b, n):
    """超椭圆极坐标半径: n=2 椭圆, n=6 圆角矩形"""
    def f(deg):
        r = math.radians(deg)
        ct, st = abs(math.cos(r)), abs(math.sin(r))
        return ((ct / a) ** n + (st / b) ** n) ** (-1.0 / n)
    return f


def _draw(base, w, bo, bi, half, digit=None, dp=10):
    """base(deg)->半径(px, 未乘超采样); w/bo/bi 同样按 px 传入。"""
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = SIZE * SS / 2.0
    S = float(SS)
    po, pi = [], []
    for i in range(1441):
        deg = 360.0 * i / 1440.0
        delta = min(abs(((deg - k + 180) % 360) - 180) for k in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) ** 1.4 if delta < half else 0.0
        rb = base(deg) * S
        ro, ri = rb + bo * S * g, rb - (w + bi * g) * S
        if ri < 0.4 * S:
            ri = 0.4 * S
        r = math.radians(deg)
        po.append((c + ro * math.cos(r), c - ro * math.sin(r)))
        pi.append((c + ri * math.cos(r), c - ri * math.sin(r)))
    dr.polygon(po + pi[::-1], fill=W)
    if digit:
        f = font(int(dp * SS))
        bb = dr.textbbox((0, 0), digit, font=f)
        dr.text((c - (bb[2] - bb[0]) / 2 - bb[0], c - (bb[3] - bb[1]) / 2 - bb[1]),
                digit, font=f, fill=W)
    return im


def save(im, name):
    im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(ICONS, name + ".png"))


def ring(name, d, digit=None, dp=10, sat=14.8):
    R = dR(d, sat)
    w = max(1.0, 0.10 * R)
    bi = min(5.0, max(1.0, 0.55 * R - 2.6))
    save(_draw(lambda deg: R, w, 0.6, bi, 30.0, digit, dp), name)
    return R, w, bi


def lens(name, a, b, w=1.7, bi=1.5, half=27, n=2.2):
    save(_draw(_shape(a, b, n), w, 0.4, bi, half), name)


def rect(name, a, b, w=1.6, bi=1.3, half=26, n=5.5):
    save(_draw(_shape(a, b, n), w, 0.4, bi, half), name)


def truss(name, R=13.0, stroke=1.3):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = SIZE * SS / 2.0
    R, st = R * SS, int(stroke * SS)
    pts = [(c + R * math.cos(math.radians(k)), c - R * math.sin(math.radians(k)))
           for k in range(0, 360, 45)]
    dr.polygon(pts, outline=W, width=st)
    for i in range(4):
        dr.line([pts[i], pts[(i + 4) % 8]], fill=W, width=int(st * 0.8))
    save(im, name)


# ---- 直径档 ----
RINGS = [("cs_size0p5", 0.9375, None, 0), ("cs_size1p2", 1.5, None, 0),
         ("cs_size1p8", 2.25, None, 0), ("cs_size2p5", 3.125, None, 0),
         ("cs_size3p5", 4.375, None, 0), ("cs_size4p5", 5.625, None, 0),
         ("cs_size5p5", 6.875, "5.5", 9), ("cs_size6p5", 8.125, "6.5", 9),
         ("cs_size7p5", 9.375, "7.5", 9)]
for n, d, dg, dp in RINGS:
    R, w, bi = ring(n, d, dg, dp)
    print(f"{n:<14} d={d:<7} R={R:5.2f}  stroke={w:4.2f}  nubIn={bi:4.2f}")

# ---- Mk 机身族(透镜形) ----
lens("cs_mk0", 8.5, 5.3)
lens("cs_mk1p5", 11.0, 6.8)
lens("cs_mk2h", 12.6, 9.6)
# ---- Mk3 / 容器族(圆角矩形) ----
rect("cs_mk3s0", 7.6, 9.6)
rect("cs_mk3s1", 9.1, 11.6)
rect("cs_mk3s1p5", 10.6, 13.6)
rect("cs_container", 10.2, 7.6)
rect("cs_vehicle", 12.2, 6.6)
# ---- 桁架 ----
truss("cs_spinaltruss")

print("\n新造完成, Icons/ 共:", len(os.listdir(ICONS)))