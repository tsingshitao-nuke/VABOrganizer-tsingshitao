"""CBP 图标生成器 v2
风格来源(实测): Squad/PartList/SimpleIcons/*.png(原版) + FilterExtensions cs_*.dds
规则:
  - 直径档   : 圆环 + 四向凸齿, 环外径 R = min(14.8, 7+3*log2(d/1.25)) px
               环径饱和的档位在环内嵌数字区分
  - Mk 机身族: 取原版 cs_mk3 / cs_mk2 轮廓按"尺寸档"等比缩放(用户要求, 不画圆)
  - 方形容器 : 圆角矩形
  - 桁架     : 八角桁架
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

SS, SIZE = 8, 32
W = (255, 255, 255, 255)
CB = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP"
ICONS = os.path.join(CB, "Icons")
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")
FONTS = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]

os.makedirs(ICONS, exist_ok=True)


def font(px):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_text(dr, c, s, px):
    f = font(int(px * SS))
    bb = dr.textbbox((0, 0), s, font=f)
    dr.text((c - (bb[2] - bb[0]) / 2 - bb[0], c - (bb[3] - bb[1]) / 2 - bb[1]),
            s, font=f, fill=W)


def save(im, name):
    im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(ICONS, name + ".png"))


def R_of(d, sat=14.8):
    return min(sat, max(3.0, 7.0 + 3.0 * math.log2(d / 1.25)))


def _clover(R, w, bo, bi, half):
    c = SIZE * SS / 2.0
    po, pi = [], []
    for i in range(1441):
        a = 360.0 * i / 1440.0
        delta = min(abs(((a - k + 180) % 360) - 180) for k in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) ** 1.4 if delta < half else 0.0
        rb = R * SS
        ro = rb + bo * SS * g
        ri = max(rb - (w + bi * g) * SS, 0.4 * SS)
        r = math.radians(a)
        po.append((c + ro * math.cos(r), c - ro * math.sin(r)))
        pi.append((c + ri * math.cos(r), c - ri * math.sin(r)))
    return po + pi[::-1], c


def ring(name, d, digit=None, dp=None):
    R = R_of(d)
    w = max(1.0, 0.10 * R)
    bi = min(5.0, max(1.0, 0.55 * R - 2.6))
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    poly, c = _clover(R, w, 0.6, bi, 30.0)
    dr.polygon(poly, fill=W)
    if digit:
        draw_text(dr, c, digit, dp or (11 if len(digit) <= 2 else 9))
    save(im, name)
    return R


MK3_REF_D, MK2_REF_D = 3.5, 2.4


def scaled_mask(name, src, sx, sy):
    m = Image.open(src).convert("RGBA")
    bb = m.getchannel("A").getbbox()
    crop = m.crop(bb)
    nw = max(3, int(round(crop.width * sx)))
    nh = max(3, int(round(crop.height * sy)))
    small = crop.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(small, ((SIZE - nw) // 2, (SIZE - nh) // 2), small)
    canvas.save(os.path.join(ICONS, name + ".png"))


def mk3_family(name, d):
    k = (R_of(d, 99) / R_of(MK3_REF_D, 99)) ** 0.75
    scaled_mask(name, os.path.join(VAN, "cs_mk3.png"), k, k)


def _shape(a, b, n):
    def f(deg):
        r = math.radians(deg)
        ct, st = abs(math.cos(r)), abs(math.sin(r))
        return ((ct / a) ** n + (st / b) ** n) ** (-1.0 / n)
    return f


def rect(name, a, b, w=1.6, bi=1.3, half=26, n=5.5):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = SIZE * SS / 2.0
    base = _shape(a, b, n)
    po, pi = [], []
    for i in range(1441):
        deg = 360.0 * i / 1440.0
        delta = min(abs(((deg - k + 180) % 360) - 180) for k in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) ** 1.4 if delta < half else 0.0
        rb = base(deg) * SS
        ro, ri = rb + 0.4 * SS * g, max(rb - (w + bi * g) * SS, 0.4 * SS)
        r = math.radians(deg)
        po.append((c + ro * math.cos(r), c - ro * math.sin(r)))
        pi.append((c + ri * math.cos(r), c - ri * math.sin(r)))
    dr.polygon(po + pi[::-1], fill=W)
    save(im, name)


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


def letter_ring(name, ch, R=10.5, dp=12):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    poly, c = _clover(R, 1.2, 0.6, 3.2, 30.0)
    dr.polygon(poly, fill=W)
    draw_text(dr, c, ch, dp)
    save(im, name)


print("== 直径档 ==")
RINGS = [("cs_size0p5", 0.9375, None), ("cs_size1h", 1.24, "h"),
         ("cs_size1p2", 1.5, None), ("cs_size1p8", 2.25, None),
         ("cs_size2p5", 3.125, None), ("cs_size3p5", 4.375, None),
         ("cs_size4p5", 5.625, "4.5"), ("cs_size5p5", 6.875, "5.5"),
         ("cs_size6p5", 8.125, "6.5"), ("cs_size7p5", 9.375, "7.5"),
         ("cs_size8p8", 11.0, "8.8"), ("cs_size12", 15.0, "12"),
         ("cs_size16", 20.0, "16"), ("cs_size24", 30.0, "24")]
for n, d, dg in RINGS:
    print(f"  {n:<14} d={d:<7} R={ring(n, d, dg):5.2f}  digit={dg}")

print("== Mk 族(原版形状按尺寸档缩放) ==")
for n, d in [("cs_mk0", 0.6), ("cs_mk3s0", 0.625), ("cs_mk3s1", 1.25),
             ("cs_mk3s1p5", 1.875), ("cs_mk1p5", 1.8)]:
    mk3_family(n, d)
    k = (R_of(d, 99) / R_of(MK3_REF_D, 99)) ** 0.75
    print(f"  {n:<14} Mk3 形状 @ {d}m 档   scale={k:.3f}")
scaled_mask("cs_mk3saddle", os.path.join(VAN, "cs_mk3.png"), 0.97, 0.84)
scaled_mask("cs_mk2h", os.path.join(VAN, "cs_mk2.png"), 0.95, 0.55)
print("  cs_mk3saddle (Mk3 压扁) / cs_mk2h (Mk2 压扁)")

print("== 矩形 / 桁架 / 分组 ==")
rect("cs_container", 10.2, 7.6)
rect("cs_vehicle", 12.2, 6.6)
rect("cs_planetarybasegarage", 12.0, 8.6)
rect("cs_circuitboard", 9.0, 4.5)
truss("cs_spinaltruss")
ring("cs_endurance", 2.9)
for n, ch in [("cs_deployable", "D"), ("cs_eva", "E"), ("cs_strut", "S")]:
    letter_ring(n, ch)
print("  完成")

print("\nIcons/ 共:", len(os.listdir(ICONS)))