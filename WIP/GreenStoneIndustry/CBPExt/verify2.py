import os, re, json, collections
from PIL import Image

BASE = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry"
CBP = os.path.join(BASE, "CBP")
ICONS = os.path.join(CBP, "Icons")
VAN = (r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
       r"\Squad\PartList\SimpleIcons")

ok = bad = 0
fails = []


def chk(cond, msg):
    global ok, bad
    if cond:
        ok += 1
    else:
        bad += 1
        fails.append(msg)


# ---- 1) 图标 ----
files = sorted(os.listdir(ICONS))
print(f"=== Icons/: {len(files)} 个 ===")
for f in files:
    im = Image.open(os.path.join(ICONS, f))
    if im.size != (32, 32):
        chk(False, f"{f} 尺寸 {im.size}")
    else:
        ok += 1
print("  全部 32x32:", all(Image.open(os.path.join(ICONS, f)).size == (32, 32) for f in files))

# ---- 2) BulkheadProfiles.cfg ----
cfg = open(os.path.join(CBP, "BulkheadProfiles.cfg"), encoding="utf-8").read()
chk(cfg.count("{") == cfg.count("}"), "定义文件括号不平衡")
defs = re.findall(r"BulkheadProfileDefinition\s*\{(.*?)\}", cfg, re.S)
print(f"\n=== BulkheadProfiles.cfg: {len(defs)} 条 ===")
names = []
bad_icon = []
for d in defs:
    n = re.search(r"name\s*=\s*(\S+)", d).group(1)
    ni = re.search(r"normalIcon\s*=\s*(\S+)", d).group(1)
    si = re.search(r"selectedIcon\s*=\s*(\S+)", d).group(1)
    names.append(n)
    chk(ni == si, f"{n} normalIcon != selectedIcon")
    if ni.startswith("GreenStoneIndustry/CBP/Icons/"):
        stem = ni.rsplit("/", 1)[1]
        if not any(os.path.splitext(x)[0] == stem for x in files):
            bad_icon.append((n, stem))
    elif ni.startswith("Squad/PartList/SimpleIcons/"):
        if not os.path.exists(os.path.join(VAN, ni.rsplit("/", 1)[1] + ".png")):
            bad_icon.append((n, ni))
    else:
        bad_icon.append((n, ni))
chk(not bad_icon, f"图标缺失: {bad_icon}")
print("  图标缺失:", bad_icon if bad_icon else "无")
dup = [k for k, v in collections.Counter(names).items() if v > 1]
chk(not dup, f"重复定义: {dup}")

# ---- 3) TokenFixes.cfg ----
tcfg = open(os.path.join(CBP, "TokenFixes.cfg"), encoding="utf-8").read()
chk(tcfg.count("{") == tcfg.count("}"), "补丁括号不平衡")
blocks = re.findall(r"@PART\[([^\]]+)\]([^\r\n]*)\r?\n\{\r?\n\s*%bulkheadProfiles\s*=\s*(.+)", tcfg)
tot = sum(len(b[0].split("|")) for b in blocks)
print(f"\n=== TokenFixes.cfg: {len(blocks)} 块, 覆盖 {tot} 部件 ===")
# 从扫描数据反推"实际被补丁归一的 token"(注释里带空格的 token 不宜用正则解析)
FIXALL = {"Size0", "Size1", "Size3", "size1.5", "size 2", "surf"}
tp = json.load(open(os.path.join(BASE, r"CBPExt\report\tokenfix_parts.json"), encoding="utf-8"))
user_parts = {"baha57mmTurret", "bahaAPS", "KRXHeronEngine", "KRX_KingEngine"}
patched = set()
for part, lst in tp.items():
    if part in user_parts:
        continue
    for _, _, toks in lst:
        patched |= {t for t in toks if t in FIXALL}
print("  实际归一的 token:", sorted(patched))

# ---- 4) 覆盖率 ----
toks = json.load(open(os.path.join(BASE, r"CBPExt\report\tokens_all.json"), encoding="utf-8"))
alltok = [t["token"] for t in toks]
VANILLA = {"srf", "size0", "size1", "size1p5", "size2", "size3", "size4",
           "mk1", "mk2", "mk3"}
USERFIX = {"Size0", "Size1", "surf"}
SKIP = {"none", "zDEPRECATED", "Airship", "Airship_Hecto", "Airship_K101",
        "Airship_Octo", "x20", "CWA_size1mk3", "CWA_size1p5mk3", "CWA_size2p5",
        "CWA_vehicle", "CWA_mk2h", "CWA_radial", "insrt"}
covered = VANILLA | set(names) | patched | USERFIX | SKIP
missing = sorted(set(alltok) - covered)
print(f"\n=== 覆盖率 (GameData 实有 token = {len(alltok)}) ===")
print(f"  KSP 原生: {len(VANILLA & set(alltok))}   本包定义: {len(set(names) & set(alltok))}"
      f"   补丁归一: {len(patched & set(alltok))}   你已修: {len(USERFIX & set(alltok))}"
      f"   有意跳过: {len(SKIP & set(alltok))}")
chk(not missing, f"未覆盖: {missing}")
print("  未覆盖:", missing if missing else "无")

# 定义里有但 GameData 没用的 token (无害, 仅提示)
extra = sorted(set(names) - set(alltok))
print("  本包多做的档位(GameData 暂未使用):", extra if extra else "无")

print(f"\n===== 通过 {ok} 项, 失败 {bad} 项 =====")
for f in fails:
    print("  FAIL", f)