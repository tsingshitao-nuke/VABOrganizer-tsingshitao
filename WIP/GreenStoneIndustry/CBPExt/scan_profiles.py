import os, re, json, collections

ROOT = r"E:\steam\steamapps\common\Kerbal Space Program\GameData"
OUT = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\report"

profile_re = re.compile(r'^\s*bulkheadProfiles\s*=\s*(.+)$', re.I | re.M)
mod_re = re.compile(r'ModuleManager\s*$')

usage = collections.defaultdict(lambda: collections.defaultdict(int))  # profile -> mod -> count
files_with_bp = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    # top-level mod name = first path segment under ROOT
    rel = os.path.relpath(dirpath, ROOT)
    mod = rel.split(os.sep)[0] if os.sep in rel else "(root)"
    for fn in filenames:
        if not fn.lower().endswith(".cfg"):
            continue
        p = os.path.join(dirpath, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            continue
        if "bulkheadProfiles" not in txt:
            continue
        files_with_bp += 1
        for m in profile_re.finditer(txt):
            val = m.group(1)
            # strip trailing comment
            val = val.split("//")[0].strip()
            for tok in val.split(","):
                tok = tok.strip()
                if not tok:
                    continue
                # ignore localizations / # keys
                if tok.startswith("#"):
                    continue
                usage[tok][mod] += 1

# also gather all module names + part names per profile for context
os.makedirs(OUT, exist_ok=True)

rows = []
for prof, mods in sorted(usage.items(), key=lambda kv: -sum(kv[1].values())):
    rows.append({
        "profile": prof,
        "total": sum(mods.values()),
        "mod_count": len(mods),
        "top_mods": sorted(mods.items(), key=lambda kv: -kv[1])[:5],
    })

with open(os.path.join(OUT, "profiles.json"), "w", encoding="utf-8") as f:
    json.dump({"files_with_bulkheadProfiles": files_with_bp, "profiles": rows}, f, indent=1, ensure_ascii=False)

print("cfg files containing bulkheadProfiles:", files_with_bp)
print("distinct profile tokens:", len(usage))
print()
print(f"{'profile':<24}{'total':>7}  {'mods':>5}  top mods")
for r in rows:
    top = ", ".join(f"{m}:{c}" for m, c in r["top_mods"][:3])
    print(f"{r['profile']:<24}{r['total']:>7}  {r['mod_count']:>5}  {top}")