"""战斗引擎冒烟测试。"""

from arena import effects, rules
from arena.battle import run_battle, turn_order
from arena.model import Combatant


def _hero():
    return Combatant(id="h1", name="Knight", hp=120, atk=37, armor=12, speed=9)


def _boss():
    return Combatant(id="b1", name="Ogre", hp=200, atk=41, armor=8, speed=7)


def test_battle_runs_to_completion():
    result = run_battle(_hero(), _boss())
    assert result["rounds"] >= 1
    assert result["log"], "战斗没有产生任何行动记录"


def test_battle_ends_with_one_side_down_or_round_limit():
    result = run_battle(_hero(), _boss(), max_rounds=5)
    assert result["rounds"] <= 5
    assert result["hero_hp"] >= 0 and result["enemy_hp"] >= 0


def test_damage_is_positive():
    hero, boss = _hero(), _boss()
    assert rules.resolve(hero, boss, 100) >= 1


def test_attack_up_increases_damage():
    hero, boss = _hero(), _boss()
    before = rules.resolve(hero, boss, 100)
    effects.apply_attack_up(hero)
    after = rules.resolve(hero, boss, 100)
    assert after > before


def test_turn_order_prefers_higher_speed():
    fast = Combatant(id="f", name="Zed", hp=10, atk=1, armor=0, speed=10)
    slow = Combatant(id="s", name="Ann", hp=10, atk=1, armor=0, speed=5)
    assert turn_order([fast, slow])[0] is fast


def test_dead_combatant_is_skipped():
    hero = _hero()
    hero.hp = 0
    result = run_battle(hero, _boss(), max_rounds=3)
    assert result["hero_hp"] == 0
    assert all(entry["actor"] != hero.id for entry in result["log"])
