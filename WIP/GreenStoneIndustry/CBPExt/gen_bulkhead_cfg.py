# -*- coding: utf-8 -*-
import os, json

CB = r"D:\my doc\GitHub\VABOrganizer-tsingshitao\WIP\GreenStoneIndustry\CBP"
DST = os.path.join(CB, "BulkheadProfiles.cfg")

# (token, displayName, icon 文件名 或 原版完整路径)
DIAM = [
    ("size00",    "Size 00 [0.3125 m]", "cs_size00"),
    ("size0p5",   "Size 0.5 [0.9375 m]", "cs_size0p5"),
    ("size1h",    "Size 1h [1.24 m]",    "cs_size1h"),
    ("size1p2",   "Size 1.2 [1.5 m]",    "cs_size1p2"),
    ("size1p8",   "Size 1.8 [2.25 m]",   "cs_size1p8"),
    ("size2p5",   "Size 2.5 [3.125 m]",  "cs_size2p5"),
    ("size3p5",   "Size 3.5 [4.375 m]",  "cs_size3p5"),
    ("size4p5",   "Size 4.5 [5.625 m]",  "cs_size4p5"),
    ("size5",     "Size 5 [6.25 m]",     "cs_size5"),
    ("size5p5",   "Size 5.5 [6.875 m]",  "cs_size5p5"),
    ("size6",     "Size 6 [7.5 m]",      "cs_size6"),
    ("size6p5",   "Size 6.5 [8.125 m]",  "cs_size6p5"),
    ("size7",     "Size 7 [8.75 m]",     "cs_size7"),
    ("size7p5",   "Size 7.5 [9.375 m]",  "cs_size7p5"),
    ("size8",     "Size 8 [10 m]",       "cs_size8"),
    ("size8p8",   "Size 8.8 [11 m]",     "cs_size8p8"),
    ("size12",    "Size 12 [15 m]",      "cs_size12"),
    ("size16",    "Size 16 [20 m]",      "cs_size16"),
    ("size24",    "Size 24 [30 m]",      "cs_size24"),
]

MK = [
    ("mk0",        "Mk 0 [0.6 m]",        "cs_mk0"),
    ("mk1",        "Mk 1 [1.25 m]",       "Squad/PartList/SimpleIcons/cs_size1"),
    ("mk1p5",      "Mk 1.5 [1.8 m]",      "cs_mk1p5"),
    ("mk2h",       "Mk 2-H [2.39 m]",     "cs_mk2h"),
    ("mk3s0",      "Mk 3-S0 [0.625 m]",   "cs_mk3s0"),
    ("mk3s1",      "Mk 3-S1 [1.25 m]",    "cs_mk3s1"),
    ("mk3s1p5",    "Mk 3-S1.5 [1.875 m]", "cs_mk3s1p5"),
    ("mk3saddle",  "Mk 3 Saddle [3.4 m]", "cs_mk3saddle"),
    ("mk4",        "Mk 4 [4.75 m]",       "cs_mk4"),
]

SHAPE = [
    ("PlanetaryBase",       "Planetary Base [2.1 m]",        "cs_kpbs"),
    ("PlanetaryBaseGarage", "Planetary Base Garage [3.3 m]", "cs_planetarybasegarage"),
    ("Container",           "Container [1.32 m]",            "cs_container"),
    ("vehicle",             "Vehicle [11 m]",                "cs_vehicle"),
    ("CircuitBoard",        "Circuit Board [0.18 m]",        "cs_circuitboard"),
    ("hextruss",            "Hex Truss [2.5 m]",             "cs_hextruss"),
    ("octotruss",           "Octo Truss [2.5 m]",            "cs_octotruss"),
    ("spinaltruss",         "Spinal Truss [3.55 m]",         "cs_spinaltruss"),
    ("procedural",          "Procedural [10 m]",             "cs_proc"),
    ("endurance",           "Endurance [2.9 m]",             "cs_endurance"),
    ("deployable",          "Deployable",                    "cs_deployable"),
    ("eva",                 "EVA",                           "cs_eva"),
    ("strut",               "Strut",                         "cs_strut"),
]

HDR = """// ============================================================================
//  GreenStoneIndustry / CBP  --  bulkhead profile definitions
//  图标目录: GreenStoneIndustry/CBP/Icons/
//
//  为 GameData 中实际出现的 bulkhead profile 档位补图标与提示文字。
//  KSP 原生已带图标的档位(srf / size0~4 / size1p5 / mk1 / mk2 / mk3)不重复定义。
//  需要 CustomBulkheadProfiles 插件才能生效(本包不含插件本体)。
//
//  直径取 VABOrganizer 全库 ORGANIZERBULKHEAD 定义值。
//  Mk 系(mk0 / mk3s* / mk3saddle / mk1p5 / mk2h)图标由原版 Mk3 / Mk2 轮廓
//  按对应尺寸档等比缩放而来, 非另画。
// ============================================================================

"""

L = [HDR]

for title, rows in [("直径档", DIAM), ("Mk 机身族", MK), ("厂商专用 / 特殊", SHAPE)]:
    bar = "-" * max(4, 74 - len(title))
    L.append(f"// {bar} {title} ----\n")
    for tok, disp, icon in rows:
        if "/" in icon:
            p = icon
        else:
            p = "GreenStoneIndustry/CBP/Icons/" + icon
        L.append("BulkheadProfileDefinition")
        L.append("{")
        L.append(f"    name = {tok}")
        L.append(f"    displayName = {disp}")
        L.append(f"    normalIcon = {p}")
        L.append(f"    selectedIcon = {p}")
        L.append("}\n")

txt = "\n".join(L)
open(DST, "w", encoding="utf-8", newline="\r\n").write(txt)
n = txt.count("BulkheadProfileDefinition")
print(f"写出 {DST}")
print(f"定义条数: {n}    文件行数: {len(txt.splitlines())}")
print(f"括号: {{ = {txt.count('{')}   }} = {txt.count('}')}")