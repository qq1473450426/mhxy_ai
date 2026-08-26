from engine.team import DEFAULT_5_ACCOUNT_TEAM
from engine.team_coordinator import TeamCoordinator


def test_team_pauses_on_member_error():
    coordinator = TeamCoordinator(DEFAULT_5_ACCOUNT_TEAM)
    result = coordinator.update_member(3, "STUCK", reason="移动超时")
    assert result.status == "PAUSED"
    assert any(item["account_id"] == 3 for item in result.actions)


def test_team_resumes_after_recovery():
    coordinator = TeamCoordinator(DEFAULT_5_ACCOUNT_TEAM)
    coordinator.update_member(3, "STUCK", reason="移动超时")
    coordinator.update_member(3, "READY")
    result = coordinator.resume_if_ready()
    assert result.status == "READY"
