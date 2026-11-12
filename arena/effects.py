"""增益与减益。"""

from arena.model import Combatant

MAX_ATTACK_UP_STACKS = 3


def apply_attack_up(target: Combatant, turns: int = 2) -> None:
    """施加一层攻击增益。"""
    target.attack_up_stacks = min(target.attack_up_stacks + 1, MAX_ATTACK_UP_STACKS)
    target.attack_up_turns = turns


def tick_buffs(target: Combatant) -> None:
    """回合结束时衰减增益。"""
    if target.attack_up_turns > 0:
        target.attack_up_turns -= 1
        if target.attack_up_turns == 0:
            target.attack_up_stacks = 0
