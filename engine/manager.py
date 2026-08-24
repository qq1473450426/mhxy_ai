import threading,time,subprocess,os
from django.utils import timezone
from dashboard.models import Worker,Log
from .window_manager import find_window,launch_game

class WorkerManager:
    def __init__(self): self.threads={}
    def log(self,a,event,msg,level='INFO'): Log.objects.create(account=a,level=level,event=event,message=msg)
    def start(self,account):
        w,_=Worker.objects.get_or_create(account=account); w.state='STARTING';w.message='准备启动客户端';w.save();self.log(account,'START','收到启动指令')
        t=threading.Thread(target=self._run,args=(account.id,),daemon=True,name=f'mhxy-worker-{account.id}');self.threads[account.id]=t;t.start()
    def stop(self,account):
        w,_=Worker.objects.get_or_create(account=account);w.state='STOPPED';w.message='已停止';w.save();self.log(account,'STOP','Worker 已停止')
    def _run(self,account_id):
        from dashboard.models import Account
        a=Account.objects.get(pk=account_id);w=Worker.objects.get(account=a)
        try:
            info=find_window(a.hwnd,a.window_title)
            if not info:
                if not a.game_exe or not os.path.exists(a.game_exe):
                    w.state='ERROR';w.message='未找到客户端，请配置 EXE 路径';w.save();self.log(a,'LAUNCH_ERROR',w.message,'ERROR');return
                p=launch_game(a.game_exe,a.launch_args);w.pid=p.pid;w.state='LOGIN';w.message='已启动客户端，等待窗口';w.save();time.sleep(3);info=find_window(a.hwnd,a.window_title)
            if not info:
                w.state='DISCONNECTED';w.message='启动后未找到窗口';w.save();self.log(a,'WINDOW_MISSING',w.message,'WARN');return
            w.state='IDLE';w.pid=info.pid;w.last_heartbeat=timezone.now();w.message='客户端窗口已连接';w.save();self.log(a,'READY','客户端窗口已连接')
        except Exception as e:
            w.state='ERROR';w.message=str(e);w.save();self.log(a,'WORKER_ERROR',str(e),'ERROR')
manager=WorkerManager()
