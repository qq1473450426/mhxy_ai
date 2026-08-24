from dataclasses import dataclass, field
from enum import Enum
import time

class WorkerState(str, Enum):
    STOPPED="STOPPED"; STARTING="STARTING"; LOGIN="LOGIN"; IDLE="IDLE"; RUNNING="RUNNING"; BATTLE="BATTLE"; DISCONNECTED="DISCONNECTED"; RECONNECTING="RECONNECTING"; ERROR="ERROR"; MANUAL_REQUIRED="MANUAL_REQUIRED"

@dataclass
class WorkerStatus:
    account_id: str
    state: WorkerState = WorkerState.STOPPED
    task_name: str = "空闲"
    last_heartbeat: float = field(default_factory=time.time)
    last_screen_change: float = field(default_factory=time.time)
    reconnect_count: int = 0
    action_count: int = 0
    error_message: str = ""
    last_ai_action: str = ""
