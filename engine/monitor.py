import time
import threading
from django.utils import timezone
from dashboard.models import Worker, Log
from .window_manager import find_window

class AccountMonitor:
    """账号级监控：窗口、心跳、掉线状态。"""
    def __init__(self, interval=2):
        self.interval=interval
        self._stop=threading.Event()
        self.thread=None

    def start(self):
        if self.thread and self.thread.is_alive(): return
        self._stop.clear(); self.thread=threading.Thread(target=self._loop,daemon=True,name='mhxy-monitor'); self.thread.start()

    def stop(self): self._stop.set()

    def _loop(self):
        from dashboard.models import Account
        while not self._stop.is_set():
            for account in Account.objects.filter(enabled=True):
                try: self.check(account)
                except Exception: pass
            time.sleep(self.interval)

    def check(self, account):
        worker,_=Worker.objects.get_or_create(account=account)
        if worker.state == 'STOPPED': return
        info=find_window(account.hwnd, account.window_title)
        if not info:
            if worker.state != 'DISCONNECTED':
                worker.state='DISCONNECTED'; worker.message='客户端窗口不存在'; worker.reconnects += 1; worker.save()
                Log.objects.create(account=account,level='WARN',event='WINDOW_LOST',message='监控发现游戏窗口消失')
            return
        worker.hwnd=info.hwnd if hasattr(worker,'hwnd') else None
        worker.pid=info.pid; worker.last_heartbeat=timezone.now()
        if worker.state == 'DISCONNECTED':
            worker.state='RECONNECTING'; worker.message='检测到窗口恢复'; Log.objects.create(account=account,event='WINDOW_RESTORED',message='游戏窗口重新出现')
        worker.save()

monitor=AccountMonitor()
