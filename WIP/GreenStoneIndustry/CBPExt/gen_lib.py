"""CBP 图标生成器 —— 复刻 KSP 原版横截面图标风格。
风格来源(实测): Squad/PartList/SimpleIcons/*.png 与 FilterExtensions cs_*.dds
  - 32x32 RGBA, 纯白 255, 透明底, 8x 超采样后 LANCZOS 降采样
  - 直径档: 圆环 + 四向凸齿(0/90/180/270), 环径 R 随直径增大
  - 顶部饱和区(size4p5 起)环径到顶, 改用环内数字区分(沿用 FE cs_size5~9 做法)
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

SS, SIZE = 8, 32
WHITE = (255, 255, 255, 255)

# ---- 实测拟合: R = 7.0 + 3.0*log2(d/1.25), 上限 15.0 ----
def R_for(d, sat=15.0):
    return min(sat, 7.0 + 3.0 * math.log2(d / 1.25))

# ---- cand-e ring params (与原版 cs_size2 视觉最接近) ----
RING_W      = 1.05      # 基础描边宽
BUMP_OUT    = 0.60      # 凸齿外扩
BUMP_IN     = 3.55      # 凸齿内加厚
BUMP_HALF   = 30.0      # 凸齿半角(度)

_FONTS = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]

def _font(px):
    for p in _FONTS:
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            continue
    return ImageFont.load_default()

def _finish(im, path):
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    im.save(path)
    return im

def _new():
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def _clover(dr, c, R, w, bo, bi, half):
    steps = 1440
    po, pi = [], []
    for i in range(steps + 1):
        a = 360.0 * i / steps
        delta = min(abs(((a - n + 180) % 360) - 180) for n in (0, 90, 180, 270))
        g = math.cos(math.pi / 2 * delta / half) ** 1.4 if delta < half else 0.0
        ro, ri = R + w / 2 + bo * g, R - w / 2 - bi * g
        rad = math.radians(a)
        po.append((c + ro * math.cos(rad), c - ro * math.sin(rad)))
        pi.append((c + ri * math.cos(rad), c - ri * math.sin(rad)))
    dr.polygon(po + pi[::-1], fill=WHITE)

def _digit(dr, c, text, px):
    f = _font(int(px * SS))
    bb = dr.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    dr.text((c - w / 2 - bb[0], c - h / 2 - bb[1]), text, font=f, fill=WHITE)

def make_ring(path, d, digit=None, sat=15.0):
    im, dr = _new()
    c = SIZE * SS / 2.0
    _clover(dr, c, R_for(d, sat) * SS, RING_W * SS, BUMP_OUT * SS, BUMP_IN * SS, BUMP_HALF)
    if digit:
        _digit(dr, c, digit, 10)
    return _finish(im, path)
