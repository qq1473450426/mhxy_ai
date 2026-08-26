from engine.battle import AutoBattleController
from engine.control import MultiOpenController
from engine.equipment import Equipment, EquipmentOptimizer


def test_single_mode_limits_to_one_account():
    class A:
        def __init__(self, i): self.id=i
    result = MultiOpenController().start([A(1), A(2)], 'single')
    assert result['account_ids'] == [1]


def test_battle_template():
    result = AutoBattleController().decide({'in_battle': True, 'rounds': 1}, 'GHOST')
    assert result['status'] == 'ACTION'
    assert result['template'] == '抓鬼'


def test_best_combat_equipment():
    items = [Equipment(1, '旧武器', '武器', 60, 50, 80, 50), Equipment(2, '新武器', '武器', 70, 55, 100, 60)]
    best = EquipmentOptimizer().best_by_slot(items, 70)
    assert best['武器'].id == 2
