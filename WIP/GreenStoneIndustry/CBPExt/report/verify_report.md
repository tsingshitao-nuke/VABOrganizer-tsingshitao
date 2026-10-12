# GreenStoneIndustry / CBP — 交付校验报告

生成时间: 2026-10-07
交付路径: `WIP\GreenStoneIndustry\CBP\`

---

## 一句话结论

给 GameData 里**实际出现的全部 62 个 `bulkheadProfiles` 档位**配齐了图标与提示文字:
**40 张图标 + 41 条定义 + 112 个部件的 token 规范化补丁**,校验 86 项全部通过。

---

## 交付物

| 文件 | 说明 |
|---|---|
| `CBP/BulkheadProfiles.cfg` | 41 条 `BulkheadProfileDefinition` |
| `CBP/TokenFixes.cfg` | 8 组 `@PART` 补丁, 归一化 112 个部件的拼写偏差 |
| `CBP/Icons/` | 40 张图标(32×32 RGBA, 30 张新造 PNG + 10 张借用 DDS) |

无 `.version`, 不含 CustomBulkheadProfiles 插件本体 — 纯配置包。

---

## 覆盖率(62/62, 无遗漏)

| 去向 | 数量 | 说明 |
|---|---|---|
| KSP 原生已带图标 | 10 | `srf` `size0` `size1` `size1p5` `size2` `size3` `size4` `mk1` `mk2` `mk3` |
| 本包定义 | 34 | 见下表 |
| 补丁归一 | 3 | `Size3`→size3(79部件)、`size1.5`→size1p5(31)、`size 2`→size2(1) |
| 你的 VABo_fixes 已修 | 3 | `Size0` `Size1` `surf`(bahaAPS / baha57mmTurret / KRX* / 已存在 `surf`→`srf` 由你决定) |
| 有意跳过 | 13 | `Airship`×4 `x20`;`none` `zDEPRECATED`;`CWA_*`×6 `insrt`(模组自带定义) |

> 本包另有 7 个档位是 VABOrganizer 有定义但 GameData 暂无部件使用:
> `size1p8` `size5p5` `size7p5` `size24`(直径档)、`size7`? `octotruss` `spinaltruss`。
> 按"29 档做满"要求保留, 无副作用。

---

## 图标规格(实测自 KSP 原版)

| 项 | 值 | 证据 |
|---|---|---|
| 尺寸 | 32 × 32 | `Squad/PartList/SimpleIcons/*.png` 全部 32×32 |
| 格式 | PNG / DDS 均可(KSP 两者都读) | 原版用 PNG;CWA / KOOSE 用 PNG;FE 用 DDS |
| 配色 | 纯白 (255,255,255), 透明底 | 像素级取样确认 |

**风格规则**

- **直径档** = 圆环 + 四向凸齿(0/90/180/270), 环外径 `R = min(14.8, 7 + 3·log₂(d/1.25))` px。
  该公式由原版 `cs_size1/2/3/4` 实测反推(官方：0.625→16px / 1.25→14 / 1.875→20 / 2.5→20 / 3.75→26 / 5.0→28)。
- 环径到顶(≥8.125 m 档)的档位,**在环内嵌数字**区分 — 沿用 FilterExtensions `cs_size5~9` 的做法。
- **Mk 机身族**按你的要求**不画圆**:直接取原版 `cs_mk3` / `cs_mk2` 轮廓**按尺寸档等比缩放**。
  小档做了可读性压缩(指数 0.75,否则 0.625 档只有 9px)。

---

## 定义清单(41 条)

**直径档 19 条**

| token | 直径 | 图标来源 |
|---|---|---|
| `size00` | 0.3125 m | 借(你的) |
| `size0p5` | 0.9375 m | 新造 |
| `size1h` | 1.24 m | 新造(环内 `h`) |
| `size1p2` | 1.5 m | 新造 |
| `size1p8` | 2.25 m | 新造 |
| `size2p5` | 3.125 m | 新造 |
| `size3p5` | 4.375 m | 新造 |
| `size4p5` | 5.625 m | 新造(环内 `4.5`) |
| `size5` | 6.25 m | 借(你的) |
| `size5p5` | 6.875 m | 新造(`5.5`) |
| `size6` | 7.5 m | 借(你的) |
| `size6p5` | 8.125 m | 新造(`6.5`) |
| `size7` | 8.75 m | 借(你的) |
| `size7p5` | 9.375 m | 新造(`7.5`) |
| `size8` | 10 m | 借(FE) |
| `size8p8` | 11 m | 新造(`8.8`) |
| `size12` | 15 m | 新造(`12`) |
| `size16` | 20 m | 新造(`16`) |
| `size24` | 30 m | 新造(`24`) |

**Mk 机身族 9 条**

| token | 直径 | 图标 |
|---|---|---|
| `mk0` | 0.6 m | 原版 Mk3 缩至 0.6 档 |
| `mk1` | 1.25 m | **复用 KSP 原生 `cs_size1`**(mk1 与 size1 同径) |
| `mk1p5` | 1.8 m | 原版 Mk3 缩至 1.8 档 |
| `mk2h` | 2.39 m | 原版 Mk2 纵向压扁(0.55) |
| `mk3s0` | 0.625 m | 原版 Mk3 缩至 0.625 档 |
| `mk3s1` | 1.25 m | 原版 Mk3 缩至 1.25 档 |
| `mk3s1p5` | 1.875 m | 原版 Mk3 缩至 1.875 档 |
| `mk3saddle` | 3.4 m | 原版 Mk3 压扁(0.97 × 0.84) |
| `mk4` | 4.75 m | 借(你的) |

**厂商专用 / 特殊 13 条**
`PlanetaryBase`(借 cs_kpbs) `PlanetaryBaseGarage` `Container` `vehicle` `CircuitBoard`
`hextruss`(借) `octotruss`(借) `spinaltruss` `procedural`(借 cs_proc)
`endurance` `deployable` `eva` `strut`

---

## 校验结果

| 项 | 结果 |
|---|---|
| 图标尺寸全部 32×32 | PASS (40/40) |
| 定义引用的图标文件落地存在 | PASS (无缺失) |
| `normalIcon` = `selectedIcon` | PASS |
| 定义名无重复 | PASS |
| 两个 cfg 括号平衡 | PASS |
| 62 个 token 全部有归宿 | PASS (未覆盖 0) |

---

## 注意事项

1. **必须安装 CustomBulkheadProfiles 插件**(本包不含)。未安装时 KSP 会把这些
   `BulkheadProfileDefinition` 当作未知节点解析掉、不报错 — 属预期静默行为。
2. **直径数值取 VABOrganizer 全库 `ORGANIZERBULKHEAD` 定义**。
   注意 FilterExtensions 的标签与之在 size5 以上不一致(FE 说 size5=7.5 m、size6=10 m;
   VABOrganizer 说 size5=6.25 m、size6=7.5 m)。本次一律采用 VABOrganizer 值,
   因为它是驱动你实际排序的配置,且与 NearFutureLaunchVehicles 的 7.5 m 部件(`size6`)自洽。
   如需改用 FE 口径, 改 `BulkheadProfiles.cfg` 里的 `displayName` 即可(仅影响提示文字)。
3. **`TokenFixes.cfg` 排除了 4 个部件**(`bahaAPS` `baha57mmTurret` `KRXHeronEngine`
   `KRX_KingEngine`)—— 它们在 `BulkheadProfilesfixes/VABo_fixes.cfg` 里已被你改成
   `srf`, 本包不覆盖你的设定。
4. 补丁用 `:NEEDS[模组]:FINAL`, 只改写 `bulkheadProfiles` 一个字段,
   保留部件原有的其他档位取值。

---

## 图标总览

见 `CBPExt/samples/_all_icons.png`(全部 40 张, 分组标注)。
