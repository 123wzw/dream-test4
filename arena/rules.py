"""伤害计算。"""

from arena.model import Combatant


def effective_armor(defender: Combatant, attacker: Combatant) -> int:
    """有效护甲。"""
    return defender.armor - attacker.pierce


def actual_atk(attacker: Combatant) -> int:
    return attacker.atk + 10 * attacker.attack_up_stacks


def base_damage(attacker: Combatant, mult_pct: int) -> int:
    """基础伤害。"""
    return round(actual_atk(attacker) * mult_pct / 100)


def resolve(attacker: Combatant, defender: Combatant, mult_pct: int) -> int:
    """结算一次普通攻击或技能。"""
    dmg = base_damage(attacker, mult_pct)
    armor = effective_armor(defender, attacker)
    if attacker.crit:
        dmg = dmg * 2 - armor
    else:
        dmg = dmg - armor
    return max(1, dmg)
