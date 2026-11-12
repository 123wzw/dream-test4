"""回合循环。"""

from arena import effects, rules
from arena.model import Combatant


def turn_order(combatants: list[Combatant]) -> list[Combatant]:
    """按速度排序，存活者参与。"""
    alive = [c for c in combatants if c.alive]
    # 稳定排序：同速保持加入战斗的先后顺序
    return sorted(alive, key=lambda c: -c.speed)


def run_battle(
    hero: Combatant,
    enemy: Combatant,
    mult_pct: int = 100,
    max_rounds: int = 20,
) -> dict:
    participants = [hero, enemy]
    log: list[dict] = []
    rounds = 0

    while rounds < max_rounds:
        rounds += 1
        acted = False
        for actor in turn_order(participants):
            if not actor.alive:
                continue
            target = next((c for c in participants if c is not actor and c.alive), None)
            if target is None:
                break
            acted = True
            damage = rules.resolve(actor, target, mult_pct)
            target.hp -= damage
            log.append(
                {
                    "round": rounds,
                    "actor": actor.id,
                    "target": target.id,
                    "damage": damage,
                    "target_hp": max(0, target.hp),
                }
            )
        for c in participants:
            if c.alive:
                effects.tick_buffs(c)
        if not acted:
            break
        if not hero.alive or not enemy.alive:
            break

    winner = None
    if hero.alive and not enemy.alive:
        winner = hero.id
    elif enemy.alive and not hero.alive:
        winner = enemy.id

    return {
        "winner": winner,
        "rounds": rounds,
        "log": log,
        "hero_hp": max(0, hero.hp),
        "enemy_hp": max(0, enemy.hp),
    }
