import re

DLL = r"E:\steam\steamapps\common\Kerbal Space Program\KSP_x64_Data\Managed\Assembly-CSharp.dll"
b = open(DLL, "rb").read()
print("dll size", len(b))

for key in [b"SimpleIcons", b"PartList", b"cs_"]:
    idxs = [m.start() for m in re.finditer(re.escape(key), b)]
    print(f"\n=== {key.decode()} : {len(idxs)} hits ===")
    for i in idxs[:6]:
        seg = b[max(0, i - 150): i + 220]
        txt = "".join(chr(c) if 32 <= c < 127 else "." for c in seg)
        print("   ...", txt)

# all cs_xxx tokens inside dll
toks = sorted(set(x.decode() for x in re.findall(rb"cs_[A-Za-z0-9_]{1,16}", b)))
print("\n=== DLL 内所有 cs_* 字面量 ===")
print(toks)