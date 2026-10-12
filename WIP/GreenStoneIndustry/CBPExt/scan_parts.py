import os, re, json, collections

ROOT = r"E:\steam\steamapps\common\Kerbal Space Program\GameData"

bp_re    = re.compile(r'^\s*bulkheadProfiles\s*=\s*(.+)$', re.I | re.M)
rescale_re = re.compile(r'^\s*rescaleFactor\s*=\s*([\d.]+)', re.I | re.M)
radius_re  = re.compile(r'^\s*(outer|radius)\s*=\s*([\d.]+)', re.I | re.M)
width_re   = re.compile(r'^\s*(width|diameter)\s*=\s*([\d.]+)', re.I | re.M)

# profile -> diameter(m) table from VABOrganizer (authoritative, already in GameData)
ORG = r"E:\steam\steamapps\common\Kerbal Space Program\GameData\VABOrganizer\bulkheadProfiles.cfg"
size_map = {}
cur = {}
for line in open(ORG, encoding='utf-8', errors='ignore'):
    m = re.match(r'\s*name\s*=\s*(\S+)', line)
    if m: cur['name'] = m.group(1)
    m = re.match(r'\s*Size\s*=\s*([\d.]+)', line, re.I)
    if m and 'name' in cur:
        size_map[cur['name']] = float(m.group(1))

# collect part name -> profiles, plus rescaleFactor
prof_parts = collections.defaultdict(list)   # profile -> [(part, rescale, mod)]
resc_by_part = {}

for dirpath, dirnames, filenames in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT)
    mod = rel.split(os.sep)[0] if os.sep in rel else "(root)"
    for fn in filenames:
        if not fn.lower().endswith(".cfg"): continue
        p = os.path.join(dirpath, fn)
        try: txt = open(p, encoding='utf-8', errors='ignore').read()
        except Exception: continue
        if 'bulkheadProfiles' not in txt: continue

        # split into PART blocks (only top-level-ish)
        for blk in re.split(r'(?m)^\s*PART\s*$', txt)[1:]:
            nm = re.search(r'(?m)^\s*name\s*=\s*(\S+)', blk)
            if not nm: continue
            pname = nm.group(1).strip('{}')
            rs = rescale_re.search(blk)
            rs = float(rs.group(1)) if rs else 1.0
            for m in bp_re.finditer(blk):
                v = m.group(1).split('//')[0].strip()
                for tok in v.split(','):
                    tok = tok.strip()
                    if not tok or tok.startswith('#'): continue
                    prof_parts[tok].append((pname, rs, mod))

rows = []
for prof, lst in sorted(prof_parts.items(), key=lambda kv: -len(kv[1])):
    d = size_map.get(prof)
    nm = size_map.get(prof.lower())
    rows.append({
        "profile": prof,
        "parts": len(lst),
        "mods": len(set(x[2] for x in lst)),
        "declared_diameter_m": d if d is not None else (size_map.get(prof.lower()) if nm else None),
        "top_mods": collections.Counter(x[2] for x in lst).most_common(4),
        "sample_parts": [x[0] for x in lst[:3]],
    })

out = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBPExt\report\profiles_full.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(rows, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print(f"{'profile':<20}{'parts':>7}{'mods':>6}{'diam(m)':>10}  top mods")
for r in rows:
    dm = r['declared_diameter_m']
    dms = f"{dm:.4g}" if dm else "--"
    print(f"{r['profile']:<20}{r['parts']:>7}{r['mods']:>6}{dms:>10}  " +
          ", ".join(f"{m}:{c}" for m, c in r['top_mods'][:3]))