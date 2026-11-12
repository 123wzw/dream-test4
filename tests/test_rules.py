"""对照 docs/RULES.md 的规则符合性测试。

每个用例对应 RULES.md 中的一条规则；当前实现与规则不一致时这些测试必须失败。
"""

from arena import effects, rules
from arena.battle import turn_order
from arena.model import Combatant


def _attacker(**kw):
    base = dict(id="a", name="Atk", hp=100, atk=50, armor=0, speed=5)
    base.update(kw)
    return Combatant(**base)


def _defender(**kw):
    base = dict(id="d", name="Def", hp=100, atk=10, armor=10, speed=5)
    base.update(kw)
    return Combatant(**base)


# RULES §2: 有效护甲 = max(0, 护甲 - 穿透)，不允许为负，
# 穿透高于护甲时多出的部分不转化为额外伤害。
def test_effective_armor_never_negative():
    atk = _attacker(pierce=30)
    dfn = _defender(armor=10)
    assert rules.effective_armor(dfn, atk) == 0


def test_excess_pierce_grants_no_bonus_damage():
    # 护甲 10、穿透 30 与穿透 10 的最终伤害应当相同
    dfn = _defender(armor=10)
    dmg_exact = rules.resolve(_attacker(pierce=10), dfn, 100)
    dmg_over = rules.resolve(_attacker(pierce=30), dfn, 100)
    assert dmg_over == dmg_exact


# RULES §3: 基础伤害 = 实际攻击力 × 技能倍率 ÷ 100，向下取整（整除），
# 不得四舍五入，不得使用浮点数参与中间计算。
def test_base_damage_floors_not_rounds():
    # 55 × 130 ÷ 100 = 71.5 → 向下取整为 71；四舍五入（含银行家舍入）会给 72
    atk = _attacker(atk=55)
    assert rules.base_damage(atk, 130) == 71
    # 55 × 170 ÷ 100 = 93.5 → 93
    assert rules.base_damage(atk, 170) == 93


def test_base_damage_uses_integer_math():
    # 55 × 105 ÷ 100 = 57.75 → 57；浮点 round 可能受精度影响，规则要求整除
    atk = _attacker(atk=55)
    assert rules.base_damage(atk, 105) == 57


# RULES §4: 先扣护甲再暴击翻倍：最终伤害 = max(1, (基础伤害 - 有效护甲) × 2)
def test_crit_doubles_after_armor_reduction():
    atk = _attacker(atk=50, crit=True)
    dfn = _defender(armor=10)
    # 基础 50，减甲 40，暴击翻倍 80；旧实现 50×2-10=90
    assert rules.resolve(atk, dfn, 100) == 80


def test_crit_still_respects_minimum_one_damage():
    atk = _attacker(atk=10, crit=True)
    dfn = _defender(armor=50)
    # 基础 10，减甲后 max(1, -40) = 1，翻倍后 2
    assert rules.resolve(atk, dfn, 100) == 2


# RULES §5: attack_up 最多 3 层，超过不再增加；重复施加刷新剩余回合为 2。
def test_attack_up_caps_at_three_stacks():
    c = _attacker()
    for _ in range(5):
        effects.apply_attack_up(c)
    assert c.attack_up_stacks == 3


def test_attack_up_refresh_keeps_two_turns():
    c = _attacker()
    effects.apply_attack_up(c)
    effects.tick_buffs(c)
    assert c.attack_up_turns == 1
    effects.apply_attack_up(c)
    assert c.attack_up_turns == 2
    assert c.attack_up_stacks == 2


def test_attack_up_expiry_clears_all_stacks():
    c = _attacker()
    for _ in range(3):
        effects.apply_attack_up(c)
    effects.tick_buffs(c)
    effects.tick_buffs(c)
    assert c.attack_up_stacks == 0
    assert c.attack_up_turns == 0


# RULES §6: speed 相同时按加入战斗的先后顺序（稳定排序），不得按名字或 ID 排序。
def test_same_speed_keeps_insertion_order():
    zed = Combatant(id="z", name="Zed", hp=10, atk=1, armor=0, speed=5)
    ann = Combatant(id="a", name="Ann", hp=10, atk=1, armor=0, speed=5)
    # Zed 先加入，虽然名字排在 Ann 后面，仍应先出手
    order = turn_order([zed, ann])
    assert order[0] is zed
    assert order[1] is ann
