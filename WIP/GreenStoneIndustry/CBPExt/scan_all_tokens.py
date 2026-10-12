import os, re, collections, json

ROOT = r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\report"

# 匹配任意位置的 bulkheadProfiles = X (含 PART 与 @PART/@MODULE 补丁)
line_re = re.compile(r'bulkheadProfiles\s*=\s*([^/\r\n]*)', re.I)

tok_mods = collections.defaultdict(collections.Counter)

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
        for m in line_re.finditer(txt):
            raw = m.group(1)
            raw = raw.replace("{", " ").replace("}", " ")
            for t in raw.split(","):
                t = t.strip()
                if t and not t.startswith("#"):
                    tok_mods[t][mod] += 1

rows = []
for t, mods in tok_mods.items():
    rows.append((t, sum(mods.values()), len(mods), mods.most_common(3)))
rows.sort(key=lambda r: (-r[1], r[0]))

os.makedirs(OUT, exist_ok=True)
json.dump([{"token": t, "count": c, "mods": n,
            "top": [[m, k] for m, k in top]} for t, c, n, top in rows],
          open(os.path.join(OUT, "tokens_all.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"distinct token: {len(rows)}\n")
print(f"{'token':<24}{'cnt':>6}{'mods':>6}  top")
print("-" * 84)
for t, c, n, top in rows:
    print(f"{t:<24}{c:>6}{n:>6}  " + ", ".join(f"{m}:{k}" for m, k in top))