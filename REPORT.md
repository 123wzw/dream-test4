# 战斗数值对齐报告

对照 `docs/RULES.md`（唯一权威定义）逐条检查 `arena/` 四个模块，共确认 **5 处不一致**，全部修复。`tests/test_rules.py` 新增 10 个规则用例，修复前其中 8 个失败（另外 2 个覆盖的规则本就已正确实现，作为回归保护保留），修复后 16 个测试（含 6 个功能用例）全部通过。

## 问题 1：有效护甲允许为负

- **违反规则**：§2「有效护甲 = max(0, 护甲 - 穿透），不允许为负；穿透高于护甲时，多出部分不转化为额外伤害」
- **代码位置**：`arena/rules.py:8`（`effective_armor`）
- **当前行为**：直接返回 `armor - pierce`，穿透超过护甲时得到负数，相当于给攻击者额外加伤
- **正确行为**：`max(0, armor - pierce)`
- **修复方式**：返回值外包 `max(0, ...)`
- **测试用例**：`test_effective_armor_never_negative`、`test_excess_pierce_grants_no_bonus_damage`

## 问题 2：基础伤害用浮点四舍五入而非整除向下取整

- **违反规则**：§3「基础伤害 = 实际攻击力 × 技能倍率 ÷ 100，向下取整（整除），不得四舍五入，不得使用浮点数参与中间计算」
- **代码位置**：`arena/rules.py:17`（`base_damage`）
- **当前行为**：`round(atk * mult / 100)`，浮点中间计算 + 银行家舍入，如 55×130÷100=71.5 被舍入为 72
- **正确行为**：整数整除 `atk * mult // 100`，71.5 → 71
- **修复方式**：改为 `actual_atk(attacker) * mult_pct // 100`
- **测试用例**：`test_base_damage_floors_not_rounds`、`test_base_damage_uses_integer_math`

## 问题 3：暴击在扣护甲之前翻倍

- **违反规则**：§4「先扣护甲，再暴击翻倍，顺序不可调换；最低伤害为 1」
- **代码位置**：`arena/rules.py:24-27`（`resolve`）
- **当前行为**：暴击时 `dmg * 2 - armor`，护甲只扣一次且翻倍作用于未减甲伤害，暴击伤害偏高（50 攻 10 甲暴击得 90，应为 80）
- **正确行为**：`max(1, 基础伤害 - 有效护甲)` 之后再 `× 2`
- **修复方式**：先算 `max(1, base - armor)`，暴击时对该结果乘 2
- **测试用例**：`test_crit_doubles_after_armor_reduction`、`test_crit_still_respects_minimum_one_damage`

## 问题 4：攻击增益层数无上限

- **违反规则**：§5「attack_up 最多 3 层，超过 3 层不再增加」
- **代码位置**：`arena/effects.py:10`（`apply_attack_up`）
- **当前行为**：`attack_up_stacks += 1` 无上限，可无限叠加
- **正确行为**：层数封顶 3（`MAX_ATTACK_UP_STACKS` 已定义但未使用）；刷新回合数为 2 的逻辑原本正确，未改
- **修复方式**：`min(stacks + 1, MAX_ATTACK_UP_STACKS)`
- **测试用例**：`test_attack_up_caps_at_three_stacks`（另 `test_attack_up_refresh_keeps_two_turns`、`test_attack_up_expiry_clears_all_stacks` 验证刷新与过期清除行为，修复前后均通过）

## 问题 5：同速角色按名字排序而非加入顺序

- **违反规则**：§6「speed 相同时按加入战斗的先后顺序（稳定排序），不得按名字或 ID 排序」
- **代码位置**：`arena/battle.py:10`（`turn_order`）
- **当前行为**：排序键 `(-speed, name)`，同速时按名字字典序，导致先加入但名字靠后的角色后出手（线上反馈的同速出手顺序问题）
- **正确行为**：仅按 `-speed` 排序，利用 Python `sorted` 的稳定性保持加入顺序
- **修复方式**：排序键改为 `-c.speed`，并加注释说明依赖稳定排序
- **测试用例**：`test_same_speed_keeps_insertion_order`

## 验证

```
$ .venv\Scripts\python -m pytest -q
................                                                         [100%]
16 passed in 0.03s
```

- `tests/test_rules.py`：10 个规则用例全绿
- `tests/test_functional.py`：6 个功能用例未改动，继续全绿
- 公开接口（`Combatant` 字段、`rules.resolve` 参数、`run_battle` 参数）未变；未引入第三方依赖
