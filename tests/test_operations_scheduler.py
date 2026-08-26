from datetime import datetime

from engine.operations_scheduler import DailyProgress, NewServerDailyScheduler


def test_daily_limits_and_priority():
    scheduler = NewServerDailyScheduler()
    progress = DailyProgress("2026-08-26", {"副本三连": 1, "师门": 20})
    task = scheduler.choose(50, progress, datetime(2026, 8, 26, 10, 0), team_ready=True)
    assert task is not None
    assert task.name == "抓鬼"


def test_leveling_until_high_level():
    scheduler = NewServerDailyScheduler()
    task = scheduler.choose(69, DailyProgress("2026-08-26"), datetime(2026, 8, 26, 10, 0), team_ready=True)
    assert task is not None
    assert task.name != "新区练级"
