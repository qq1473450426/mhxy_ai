"""五开同步协调器。

负责队长/队员的阶段状态、暂停恢复和重组计划。
不直接执行鼠标键盘动作。
"""
from dataclasses import dataclass, field
from typing import Any

from .team import TeamProfile


@dataclass
class MemberRuntime:
    account_id: int
    state: str = "READY"
    last_error: str = ""
    progress: dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamSyncResult:
    status: str
    reason: str
    actions: list[dict[str, Any]] = field(default_factory=list)


class TeamCoordinator:
    """五开任务的安全同步状态机。"""

    SAFE_STATES = {"READY", "TASK", "MOVING", "BATTLE", "COMPLETED"}
    RECOVERABLE_STATES = {"DISCONNECTED", "STUCK", "ERROR", "WINDOW_MISSING"}

    def __init__(self, profile: TeamProfile):
        self.profile = profile
        self.members = {m.account_id: MemberRuntime(m.account_id) for m in profile.active_members}
        self.paused = False

    def update_member(self, account_id: int, state: str, **progress: Any) -> TeamSyncResult:
        member = self.members.get(account_id)
        if member is None:
            return TeamSyncResult("ERROR", "账号不属于当前队伍")
        member.state = str(state).upper()
        member.progress.update(progress)
        if member.state in self.RECOVERABLE_STATES:
            self.paused = True
            member.last_error = str(progress.get("reason", member.state))
            return TeamSyncResult("PAUSED", f"账号 {account_id} 需要恢复：{member.last_error}", self.recovery_plan(account_id))
        return self.evaluate()

    def evaluate(self) -> TeamSyncResult:
        if self.paused:
            return TeamSyncResult("PAUSED", "队伍处于恢复状态")
        invalid = [m.account_id for m in self.members.values() if m.state not in self.SAFE_STATES]
        if invalid:
            return TeamSyncResult("PAUSED", f"账号状态异常：{invalid}")
        return TeamSyncResult("READY", "队伍状态一致，可以继续执行", self.profile.synchronization_plan())

    def recovery_plan(self, account_id: int) -> list[dict[str, Any]]:
        leader = self.profile.leader
        actions = [
            {"account_id": account_id, "action": "RECONNECT_OR_FOCUS_WINDOW"},
            {"account_id": account_id, "action": "RECHECK_GAME_STATE"},
        ]
        if leader and account_id != leader.account_id:
            actions.append({"account_id": account_id, "action": "REJOIN_TEAM", "leader": leader.account_id})
        else:
            actions.append({"account_id": account_id, "action": "REBUILD_TEAM"})
        actions.append({"account_id": leader.account_id if leader else account_id, "action": "VERIFY_TEAM"})
        return actions

    def resume_if_ready(self) -> TeamSyncResult:
        if any(m.state in self.RECOVERABLE_STATES for m in self.members.values()):
            return TeamSyncResult("PAUSED", "仍有账号未恢复")
        self.paused = False
        return self.evaluate()
