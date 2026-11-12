# arena-core

回合制战斗引擎核心库，供战棋和卡牌项目复用。

## 技术栈

- Python 3.12，纯标准库

## 用法

```python
from arena.model import Combatant
from arena.battle import run_battle

hero = Combatant(id="h1", name="Knight", hp=120, atk=37, armor=12, speed=9)
boss = Combatant(id="b1", name="Ogre", hp=200, atk=41, armor=8, speed=7)
result = run_battle(hero, boss)
print(result["winner"], result["rounds"])
```

## 规则

战斗数值口径见 `docs/RULES.md`，该文件是唯一权威定义。

## 目录

```
arena/model.py     角色数据结构
arena/rules.py     伤害计算
arena/effects.py   增益与减益
arena/battle.py    回合循环
docs/RULES.md      战斗规则
tests/test_functional.py  冒烟测试
```

## 测试

```bash
.venv/Scripts/python -m pytest -q
```

## 已知问题

- 数值平衡一直在调，公式改过多轮，代码可能与最新规则文档不一致。
- 同速出手顺序在多人混战时偶有争议，待策划确认。
