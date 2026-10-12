"""复刻原版横截面图标风格的核心绘制库。
原版风格(从 Squad/PartList/SimpleIcons 与 FilterExtensions 解出):
  - 32x32 RGBA,纯白 (255,255,255),透明底
  - 直径档 = 圆环 + 四向(0/90/180/270)加厚凸齿,形成四叶(clover)轮廓
  - 环外半径 R 与直径 d 近似 R = 6.26*sqrt(d)
  - 大直径档 R 饱和到 ~15.5px,改用环内嵌数字区分(FE 的 cs_size5~9 做法)
"""
import math
from PIL import Image, ImageDraw, ImageFont

SS = 8                 # 超采样倍数
SIZE = 32
WHITE = (255, 255, 255, 255)

_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]


def _font(px):
    for p in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            continue
    return ImageFont.load_default()


def R_for(d, sat=15.5):
    """直径(m) -> 环外半径(px @32px canvas)"""
    return min(sat, 6.26 * math.sqrt(d))


def _new():
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _finish(im, path):
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    im.save(path)
    return im


def _ring(dr, cx, cy, R, w, fill=WHITE, steps=720, nubs=None,
          nub_half=22.0, nub_extra=1.9, nub_r_out=0.6):
    """画圆环。nubs: 凸齿中心角度列表(度);凸齿处描边加粗并略外凸。"""
    if nubs is None:
        nubs = [0, 90, 180, 270]
    pts_out, pts_in = [], []
    for i in range(steps + 1):
        a = 360.0 * i / steps
        rad = math.radians(a)
        r_out, r_in = R + w / 2.0, R - w / 2.0
        # 凸齿:角度落在 nub 半宽内 -> 外扩 + 加厚
        best = min((abs(((a - n + 180) % 360) - 180) for n in nubs), default=999)
        if best < nub_half:
            k = math.cos(math.pi / 2 * best / nub_half)   # 1->0 平滑
            r_out += nub_r_out * k
            r_in -= nub_extra * k
        pts_out.append((cx + r_out * math.cos(rad), cy - r_out * math.sin(rad)))
        pts_in.append((cx + r_in * math.cos(rad), cy - r_in * math.sin(rad)))
    dr.polygon(pts_out + pts_in[::-1], fill=fill)


def _digit(dr, cx, cy, text, px, fill=WHITE):
    f = _font(int(px * SS))
    bb = dr.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    dr.text((cx - w / 2 - bb[0], cy - h / 2 - bb[1]), text, font=f, fill=fill)


def make_diameter_icon(path, d, digit=None, sat=15.5):
    """直径档图标。digit=None 时不嵌数字。"""
    im, dr = _new()
    c = SIZE * SS / 2.0
    R = R_for(d, sat) * SS
    w = 2.4 * SS if digit is None else 3.2 * SS
    _ring(dr, c, c, R, w)
    if digit:
        _digit(dr, c, c, digit, 11)
    return _finish(im, path)


def make_rect_icon(path, hx, hy, w, rounded=0.45, digit=None):
    """圆角矩形轮廓(方形/容器/车辆类)"""
    im, dr = _new()
    c = SIZE * SS / 2.0
    hx, hy, w = hx * SS, hy * SS, w * SS
    r = min(hx, hy) * rounded
    dr.rounded_rectangle([c - hx, c - hy, c + hx, c + hy], radius=r,
                         outline=WHITE, width=int(w))
    if digit:
        _digit(dr, c, c, digit, 10)
    return _finish(im, path)


def make_hex_icon(path, rx, ry, w, digit=None):
    """六边形轮廓(Mk2 机身类)"""
    im, dr = _new()
    c = SIZE * SS / 2.0
    rx, ry, w = rx * SS, ry * SS, w * SS
    pts = [(c + rx, c), (c + rx * 0.45, c - ry), (c - rx * 0.45, c - ry),
           (c - rx, c), (c - rx * 0.45, c + ry), (c + rx * 0.45, c + ry)]
    dr.polygon(pts, outline=WHITE, width=int(w))
    if digit:
        _digit(dr, c, c, digit, 10)
    return _finish(im, path)


def make_clover_icon(path, d, digit=None):
    """桁架类:四叶加强环"""
    im, dr = _new()
    c = SIZE * SS / 2.0
    R = R_for(d) * SS
    _ring(dr, c, c, R, 3.0 * SS, nub_half=30, nub_extra=3.0, nub_r_out=1.2)
    if digit:
        _digit(dr, c, c, digit, 10)
    return _finish(im, path)