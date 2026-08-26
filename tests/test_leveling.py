"""新区练级策略与闭环控制器测试。"""
from engine.leveling import LevelingCandidate, NewServerLevelingStrategy
from engine.leveling_controller import NewServerLevelingController


class FakeObserver:
    def __init__(self, data):
        self.data = data

    def observe(self):
        return self.data


class FakeExecutor:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, task, observation):
        self.calls.append(task)
        return self.result


def test_stage_and_priority():
    strategy = NewServerLevelingStrategy()
    assert "抓鬼" in strategy.priority_order(50)
    assert strategy.stage_for_level(69) == "69级卡级"


def test_choose_highest_score():
    strategy = NewServerLevelingStrategy()
    result = strategy.choose(50, [
        LevelingCandidate("师门", estimated_exp=100),
        LevelingCandidate("抓鬼", estimated_exp=150, repeatability=10),
    ])
    assert result.task == "抓鬼"


def test_controller_reaches_target():
    observer = FakeObserver({"level": 69, "level_known": True, "window_available": True})
    executor = FakeExecutor({})
    result = NewServerLevelingController(observer, executor).tick()
    assert result.status == "TARGET_REACHED"
    assert executor.calls == []


def test_controller_executes_and_verifies():
    observer = FakeObserver({
        "level": 50,
        "level_known": True,
        "window_available": True,
        "candidates": [{"name": "抓鬼", "estimated_exp": 150, "repeatability": 5}],
    })
    executor = FakeExecutor({"completed": True, "level": 51, "progress": 20})
    result = NewServerLevelingController(observer, executor).tick()
    assert result.status == "COMPLETED"
    assert executor.calls == ["抓鬼"]
