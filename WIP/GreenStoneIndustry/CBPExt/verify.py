import os, re, json, collections, glob
from PIL import Image

BASE = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry"
CBP = os.path.join(BASE, "CBP")
ICONS = os.path.join(CBP, "Icons")
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")

rep = []
ok = bad = 0


def chk(cond, msg):
    global ok, bad
    if cond:
        ok += 1
    else:
        bad += 1
        rep.append("FAIL  " + msg)


# ---------- 1) 图标文件 ----------
files = sorted(os.listdir(ICONS))
print(f"=== Icons/ 共 {len(files)} 个文件 ===")
for f in files:
    p = os.path.join(ICONS, f)
    im = Image.open(p)
    sz, mode = im.size, im.mode
    fmt = im.format
    line = f"{f:<24}{fmt:<5}{sz[0]}x{sz[1]:<5}{mode}"
    if sz != (32, 32):
        line += "   <<< SIZE!"
    okk = sz == (32, 32)
    chk(okk, f"{f} 尺寸 {sz}")
    print("  " + line)

# ---------- 2) BulkheadProfiles.cfg ----------
bcfg = open(os.path.join(CBP, "BulkheadProfiles.cfg"), encoding="utf-8").read()
chk(bcfg.count("{") == bcfg.count("}"), "BulkheadProfiles.cfg 括号不平衡")
defs = re.findall(r"BulkheadProfileDefinition\s*\{(.*?)\}", bcfg, re.S)
print(f"\n=== BulkheadProfiles.cfg: {len(defs)} 条定义 ===")
names = []
for d in defs:
    n = re.search(r"name\s*=\s*(\S+)", d).group(1)
    ni = re.search(r"normalIcon\s*=\s*(\S+)", d).group(1)
    si = re.search(r"selectedIcon\s*=\s*(\S+)", d).group(1)
    mn = re.search(r"displayName\s*=\s*(.+)", d).group(1).strip()
    names.append(n)
    chk(ni == si, f"{n} normal/selected 不一致")
    if ni.startswith("GreenStoneIndustry/CBP/Icons/"):
        stem = ni.rsplit("/", 1)[1]
        found = [x for x in files if os.path.splitext(x)[0] == stem]
        chk(bool(found), f"{n} 图标缺失: {ni}")
        tag = found[0] if found else "!!MISSING!!"
    elif ni.startswith("Squad/PartList/SimpleIcons/"):
        stem = ni.rsplit("/", 1)[1] + ".png"
        chk(os.path.exists(os.path.join(VAN, stem)), f"{n} 原版图标缺失: {ni}")
        tag = "[vanilla] " + stem
    else:
        tag = "??"
        chk(False, f"{n} 未知图标来源: {ni}")
    print(f"  {n:<16}{mn:<26}{tag}")

dup = [k for k, v in collections.Counter(names).items() if v > 1]
chk(not dup, f"重复定义名: {dup}")

# ---------- 3) TokenFixes.cfg ----------
tcfg = open(os.path.join(CBP, "TokenFixes.cfg"), encoding="utf-8").read()
chk(tcfg.count("{") == tcfg.count("}"), "TokenFixes.cfg 括号不平衡")
blocks = re.findall(r"@PART\[([^\]]+)\]([^\r\n]*)\r?\n\{\r?\n\s*%bulkheadProfiles\s*=\s*(.+)", tcfg)
print(f"\n=== TokenFixes.cfg: {len(blocks)} 个 @PART 块 ===")
tot = 0
for parts, mods, val in blocks:
    n = len(parts.split("|"))
    tot += n
    print(f"  {len(parts.split('|')):>3} parts  ->  {val.strip():<18}{mods.strip()}")
print(f"  合计覆盖部件: {tot}")

# ---------- 4) 覆盖率: 44 个 token 的去向 ----------
prof = json.load(open(os.path.join(BASE, r"CBPExt\report\profiles.json"), encoding="utf-8"))
tokens = {r["profile"] for r in prof["profiles"]}
VANILLA = {"srf", "size0", "size1", "size1p5", "size2", "size3", "size4",
           "mk1", "mk2", "mk3"}
PATCH = set()
for parts, mods, val in blocks:
    pass
patched_tokens = set()
for line in tcfg.splitlines():
    m = re.match(r"//\s*(\S+?)->(\S+?)\s+==>", line)
    if m:
        patched_tokens.add(m.group(1))
SKIP = {"none", "zDEPRECATED", "Airship", "Airship_Hecto", "Airship_K101",
        "Airship_Octo", "x20", "CWA_size1mk3", "CWA_size1p5mk3",
        "CWA_size2p5", "CWA_vehicle", "CWA_mk2h", "CWA_radial", "insrt"}

covered = VANILLA | set(names) | patched_tokens | SKIP
missing = sorted(tokens - covered)
print(f"\n=== 覆盖率 ===")
print(f"  GameData 实有 token: {len(tokens)}")
print(f"  KSP 原生覆盖: {len(VANILLA & tokens)}  本包定义: {len(set(names) & tokens)}"
      f"  补丁归一: {len(patched_tokens)}  有意跳过: {len(SKIP & tokens)}")
chk(not missing, f"未覆盖 token: {missing}")
print(f"  未覆盖: {missing if missing else '无'}")
print(f"  补丁归一 token: {sorted(patched_tokens)}")

print(f"\n===== 校验结果: 通过 {ok} 项, 失败 {bad} 项 =====")
for r in rep:
    print(r)