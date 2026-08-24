from dataclasses import dataclass
from enum import Enum

class State(str,Enum):
    STOPPED='STOPPED'; STARTING='STARTING'; LOGIN='LOGIN'; IDLE='IDLE'; NAVIGATING='NAVIGATING'; BATTLE='BATTLE'; TASK='TASK'; DISCONNECTED='DISCONNECTED'; RECONNECTING='RECONNECTING'; ERROR='ERROR'

@dataclass
class Transition:
    state: State
    action: str
    progress: int
    message: str

class RuntimeStateMachine:
    def __init__(self): self.state=State.STOPPED
    def next(self, observation: dict)->Transition:
        """确定性状态机；视觉/Skill 层只提供 observation，不在此处猜测游戏内部状态。"""
        s=observation.get('state')
        if s in State._value2member_map_: self.state=State(s)
        actions={
            State.STARTING:('启动客户端',0,'等待窗口'),
            State.LOGIN:('等待登录',5,'等待账号登录完成'),
            State.IDLE:('待机',10,'等待任务'),
            State.NAVIGATING:('自动寻路',30,'按 Skill 路线执行'),
            State.BATTLE:('自动战斗',60,'按战斗 Skill 执行'),
            State.TASK:('执行日常任务',80,'执行任务步骤'),
            State.DISCONNECTED:('掉线处理',0,'等待重连'),
            State.RECONNECTING:('重新连接',0,'恢复客户端'),
            State.ERROR:('异常停止',0,'等待人工处理'),
            State.STOPPED:('已停止',0,'Worker 已停止'),
        }
        action,p,msg=actions[self.state]
        return Transition(self.state,action,p,msg)
