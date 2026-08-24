from .models import WorkerState

TRANSITIONS={
WorkerState.STOPPED:{WorkerState.STARTING},WorkerState.STARTING:{WorkerState.LOGIN,WorkerState.ERROR},WorkerState.LOGIN:{WorkerState.IDLE,WorkerState.DISCONNECTED,WorkerState.ERROR},WorkerState.IDLE:{WorkerState.RUNNING,WorkerState.DISCONNECTED,WorkerState.ERROR,WorkerState.STOPPED},WorkerState.RUNNING:{WorkerState.BATTLE,WorkerState.IDLE,WorkerState.DISCONNECTED,WorkerState.ERROR,WorkerState.STOPPED},WorkerState.BATTLE:{WorkerState.RUNNING,WorkerState.IDLE,WorkerState.DISCONNECTED,WorkerState.ERROR,WorkerState.STOPPED},WorkerState.DISCONNECTED:{WorkerState.RECONNECTING,WorkerState.MANUAL_REQUIRED,WorkerState.STOPPED},WorkerState.RECONNECTING:{WorkerState.LOGIN,WorkerState.DISCONNECTED,WorkerState.ERROR,WorkerState.MANUAL_REQUIRED},WorkerState.ERROR:{WorkerState.RECONNECTING,WorkerState.STOPPED,WorkerState.MANUAL_REQUIRED},WorkerState.MANUAL_REQUIRED:{WorkerState.STARTING,WorkerState.STOPPED}}

def transition(current,target):
    if current==target:return current
    if target not in TRANSITIONS.get(current,set()):raise ValueError(f"非法状态迁移: {current} -> {target}")
    return target
