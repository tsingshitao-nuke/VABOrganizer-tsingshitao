import os, glob
from PIL import Image

SRC = [
    r"E:\steam\steamapps\common\Kerbal Space Program\GameData\000_FilterExtensions\Icons\Autoloaded_Icons_CrossSections",
    r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP",
]
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\decode"
os.makedirs(OUT, exist_ok=True)

seen = {}
for d in SRC:
    for f in sorted(glob.glob(os.path.join(d, "*.dds"))):
        n = os.path.basename(f)
        if n in seen:
            continue
        seen[n] = f

print(f"共 {len(seen)} 张\n")
for n, f in sorted(seen.items()):
    try:
        im = Image.open(f).convert("RGBA")
    except Exception as e:
        print(f"{n:<24} FAIL {e}")
        continue
    w, h = im.size
    # alpha stats
    a = im.getchannel("A")
    amin, amax = a.getextrema()
    hist = a.histogram()
    opaque = sum(hist[200:])
    semi = sum(hist[20:200])
    clear = sum(hist[:20])
    total = w * h
    # save upscaled preview
    im.resize((w * 8, h * 8), Image.NEAREST).save(os.path.join(OUT, n.replace(".dds", ".png")))
    print(f"{n:<24} {w}x{h}  A[{amin}-{amax}] 不透明{opaque*100//total:>3}% 半透明{semi*100//total:>3}% 透明{clear*100//total:>3}%")
print("\n预览已放大 8 倍保存到", OUT)