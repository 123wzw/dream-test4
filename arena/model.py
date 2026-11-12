"""角色数据结构。"""

from dataclasses import dataclass


@dataclass
class Combatant:
    id: str
    name: str
    hp: int
    atk: int
    armor: int
    speed: int
    pierce: int = 0
    crit: bool = False
    attack_up_stacks: int = 0
    attack_up_turns: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0
