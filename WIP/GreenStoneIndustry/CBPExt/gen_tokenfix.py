import os, re, json, collections

BASE = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry"
SRC = os.path.join(BASE, r"CBPExt\report\tokenfix_parts.json")
USERFIX = os.path.join(BASE, r"BulkheadProfilesfixes\VABo_fixes.cfg")
DST = os.path.join(BASE, r"CBP\TokenFixes.cfg")

FIX = {"Size0": "size0", "Size1": "size1", "Size3": "size3",
       "size1.5": "size1p5", "size 2": "size2", "surf": "srf"}

hits = json.load(open(SRC, encoding="utf-8"))

# --- 1) 收集用户 VABo_fixes.cfg 已处理的部件名, 这些不碰 ---
user_parts = set()
if os.path.exists(USERFIX):
    txt = open(USERFIX, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'@PART\[([^\]]+)\]', txt):
        for n in m.group(1).split("|"):
            n = n.strip()
            if n.endswith("*"):
                n = n[:-1]
            user_parts.add(n)
print("VABo_fixes 已处理部件:", sorted(user_parts))

# --- 2) 归一化每个部件的完整 bulkheadProfiles 值 ---
plan = {}          # part -> normalized full value
skipped = []       # 被用户 fix 覆盖的
conflict = []
for part, lst in hits.items():
    if part in user_parts:
        skipped.append(part)
        continue
    vals = set()
    for mod, raw, toks in lst:
        norm = [FIX.get(t, t) for t in toks]
        # 去重保序
        seen, out = set(), []
        for t in norm:
            if t not in seen:
                seen.add(t); out.append(t)
        vals.add(", ".join(out))
    if len(vals) > 1:
        conflict.append((part, sorted(vals)))
    plan[part] = sorted(vals)[0]

print(f"\n待归一化部件: {len(plan)}   已跳过(用户已修): {len(skipped)}")
if conflict:
    print("!! 同名校验冲突:", conflict)

# --- 3) 按 标准值 分组输出(needs 列全部相关模组, 逗号=任一存在即可) ---
group = collections.defaultdict(list)
for part, val in plan.items():
    group[val].append(part)

L = []
L.append("// ==========================================================================")
L.append("//  GreenStoneIndustry / CBP  --  bulkheadProfile token normalisation")
L.append("//")
L.append("//  修正其他模组 part 配置里的大小写/拼写偏差, 使其落到标准档位并继承图标:")
L.append("//      Size0 -> size0   Size1 -> size1   Size3 -> size3")
L.append("//      size1.5 -> size1p5      \"size 2\" -> size2      surf -> srf")
L.append("//  仅改写 bulkheadProfiles 一个字段, 保留部件原有的其他档位取值。")
L.append("//  已由 BulkheadProfilesfixes/VABo_fixes.cfg 处理过的部件不在本文件重复。")
L.append("// ==========================================================================")
L.append("")

total_parts = 0
for val, parts in sorted(group.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    parts = sorted(set(parts))
    total_parts += len(parts)
    # 该组涉及的原始错误 token 与涉及模组
    orig, mods = set(), set()
    for p in parts:
        for mod, raw, toks in hits[p]:
            mods.add(mod)
            for t in toks:
                if t in FIX:
                    orig.add(f"{t}->{FIX[t]}")
    L.append(f"// {'  '.join(sorted(orig))}   ==>   {val}   ({len(parts)} parts)")
    L.append(f"@PART[{ '|'.join(parts) }]:NEEDS[{','.join(sorted(mods))}]:FINAL")
    L.append("{")
    L.append(f"    %bulkheadProfiles = {val}")
    L.append("}")
    L.append("")

open(DST, "w", encoding="utf-8", newline="\r\n").write("\n".join(L))
print(f"\n写出 {DST}")
print(f"补丁块数: {len(group)}   覆盖部件: {total_parts}")
print(f"跳过(用户已修): {len(skipped)} -> {skipped}")