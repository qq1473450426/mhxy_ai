"""多开队伍编排层。

不负责具体点击，只定义队长、角色职责和同步规则，供 Worker/TaskRunner 使用。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TeamMember:
    account_id: int
    role: str
    position: int
    enabled: bool = True


@dataclass(frozen=True)
class TeamProfile:
    name: str
    members: tuple[TeamMember, ...]
    leader_account_id: int | None = None

    @property
    def leader(self):
        if self.leader_account_id is not None:
            for member in self.members:
                if member.account_id == self.leader_account_id:
                    return member
        return next((m for m in self.members if m.position == 1 and m.enabled), None)

    @property
    def active_members(self):
        return tuple(m for m in self.members if m.enabled)

    def validate(self) -> list[str]:
        errors = []
        if not self.active_members:
            errors.append("队伍没有启用账号")
        if self.leader is None:
            errors.append("队伍没有队长")
        if len({m.account_id for m in self.active_members}) != len(self.active_members):
            errors.append("队伍存在重复账号")
        if len(self.active_members) > 5:
            errors.append("当前策略最多支持5开")
        return errors

    def synchronization_plan(self) -> list[dict]:
        """生成队伍同步顺序，实际动作由 Worker 执行。"""
        leader = self.leader
        if leader is None:
            return []
        return [
            {"account_id": leader.account_id, "action": "LEAD", "order": 1},
            *[
                {"account_id": member.account_id, "action": "FOLLOW", "leader": leader.account_id, "order": member.position}
                for member in self.active_members
                if member.account_id != leader.account_id
            ],
        ]


DEFAULT_5_ACCOUNT_TEAM = TeamProfile(
    name="新区五开",
    members=(
        TeamMember(1, "辅助", 1),
        TeamMember(2, "输出", 2),
        TeamMember(3, "输出", 3),
        TeamMember(4, "输出", 4),
        TeamMember(5, "输出", 5),
    ),
    leader_account_id=1,
)
