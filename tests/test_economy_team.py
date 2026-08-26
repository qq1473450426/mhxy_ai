from engine.economy import ActivityProfile, EconomyPlanner
from engine.team import TeamMember, TeamProfile


def test_economy_rank_by_profit():
    planner = EconomyPlanner()
    result = planner.choose([
        ActivityProfile("A", expected_value=100, minutes=60),
        ActivityProfile("B", expected_value=200, minutes=60),
    ], mode="profit")
    assert result["activity"] == "B"


def test_team_validation_and_sync():
    team = TeamProfile(
        "test",
        (TeamMember(1, "leader", 1), TeamMember(2, "output", 2)),
        leader_account_id=1,
    )
    assert team.validate() == []
    plan = team.synchronization_plan()
    assert plan[0]["action"] == "LEAD"
    assert plan[1]["action"] == "FOLLOW"
