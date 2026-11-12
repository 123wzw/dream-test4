"""伤害计算。"""

from arena.model import Combatant


def effective_armor(defender: Combatant, attacker: Combatant) -> int:
    """有效护甲，不允许为负。"""
    return max(0, defender.armor - attacker.pierce)


def actual_atk(attacker: Combatant) -> int:
    return attacker.atk + 10 * attacker.attack_up_stacks


def base_damage(attacker: Combatant, mult_pct: int) -> int:
    """基础伤害，整除向下取整。"""
    return actual_atk(attacker) * mult_pct // 100


def resolve(attacker: Combatant, defender: Combatant, mult_pct: int) -> int:
    """结算一次普通攻击或技能。"""
    dmg = max(1, base_damage(attacker, mult_pct) - effective_armor(defender, attacker))
    if attacker.crit:
        dmg *= 2
    return dmg
