import os, re, json, collections

ROOT = r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\report"

# 需要规范化的 token -> 标准名
FIX = {"Size0": "size0", "Size1": "size1", "Size3": "size3",
       "size1.5": "size1p5", "size 2": "size2", "surf": "srf"}

bp_re = re.compile(r'^\s*bulkheadProfiles\s*=\s*(.+)$', re.I | re.M)
hits = collections.defaultdict(list)   # raw_part -> list of (mod, raw_value)

for dirpath, dirnames, filenames in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT)
    mod = rel.split(os.sep)[0]
    for fn in filenames:
        if not fn.endswith(".cfg"):
            continue
        p = os.path.join(dirpath, fn)
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if "bulkheadProfiles" not in txt:
            continue
        for blk in re.split(r'(?m)^\s*PART\s*$', txt)[1:]:
            nm = re.search(r'(?m)^\s*name\s*=\s*(\S+)', blk)
            if not nm:
                continue
            pname = nm.group(1).strip('\t {}')
            for m in bp_re.finditer(blk):
                raw = m.group(1).split("//")[0].strip()
                toks = [t.strip() for t in raw.split(",") if t.strip()]
                if any(t in FIX for t in toks):
                    hits[pname].append((mod, raw, toks))

os.makedirs(OUT, exist_ok=True)
json.dump(hits, open(os.path.join(OUT, "tokenfix_parts.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"命中部件数: {len(hits)}\n")
print(f"{'part':<42}{'mod':<26}raw")
print("-" * 100)
for pn in sorted(hits):
    for mod, raw, toks in hits[pn]:
        print(f"{pn:<42}{mod:<26}{raw}")

# 统计每个 token 涉及部件数
cnt = collections.Counter()
for pn, lst in hits.items():
    for _, _, toks in lst:
        for t in toks:
            if t in FIX:
                cnt[t] += 1
print("\n各 token 命中:", dict(cnt))
print("可归一化的唯一部件数:", len(hits))