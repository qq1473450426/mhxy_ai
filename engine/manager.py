import os
import threading
import time
from django.utils import timezone
from dashboard.models import Worker, Log
from .window_manager import find_window, launch_game


class WorkerManager:
    def __init__(self): self.threads = {}
    def log(self, a, event, msg, level='INFO'): Log.objects.create(account=a, level=level, event=event, message=msg)
    def start(self, account):
        w, _ = Worker.objects.get_or_create(account=account); w.state='STARTING'; w.message='准备启动客户端'; w.save(); self.log(account,'START','收到启动指令')
        t=threading.Thread(target=self._run,args=(account.id,),daemon=True,name=f'mhxy-worker-{account.id}'); self.threads[account.id]=t; t.start()
    def stop(self, account):
        w, _ = Worker.objects.get_or_create(account=account); w.state='STOPPED'; w.message='已停止'; w.save(); self.log(account,'STOP','Worker 已停止')
    def _run(self, account_id):
        from dashboard.models import Account
        from .login import login_account
        a=Account.objects.get(pk=account_id); w=Worker.objects.get(account=a)
        try:
            info=find_window(a.hwnd,a.window_title)
            if not info:
                if not a.game_exe or not os.path.exists(a.game_exe):
                    w.state='ERROR'; w.message='未找到客户端，请配置 EXE 路径'; w.save(); self.log(a,'LAUNCH_ERROR',w.message,'ERROR'); return
                p=launch_game(a.game_exe,a.launch_args); w.pid=p.pid; w.state='LOGIN'; w.message='已启动客户端，等待窗口'; w.save(); time.sleep(3); info=find_window(a.hwnd,a.window_title)
            if not info:
                w.state='DISCONNECTED'; w.message='启动后未找到窗口'; w.save(); self.log(a,'WINDOW_MISSING',w.message,'WARN'); return
            a.hwnd=info.hwnd
            w.state='LOGIN'; w.pid=info.pid; w.last_heartbeat=timezone.now(); w.message='客户端窗口已连接，准备登录'; w.save(); self.log(a,'WINDOW_READY','客户端窗口已连接')
            if not a.auto_login:
                w.state='IDLE'; w.message='客户端已启动，等待人工登录'; w.save(); self.log(a,'READY','自动登录关闭'); return
            result=login_account(a)
            if not result.get('success'):
                w.state='PAUSED' if result.get('status')=='VERIFY_REQUIRED' else 'ERROR'
                w.message='需要人工处理安全验证' if result.get('status')=='VERIFY_REQUIRED' else f"自动登录失败：{result.get('reason', result.get('status','UNKNOWN'))}"
                w.save(); self.log(a,'LOGIN_VERIFY_REQUIRED' if result.get('status')=='VERIFY_REQUIRED' else 'LOGIN_FAILED',w.message,'WARN'); return
            a.save(update_fields=['hwnd'])
            w.state='IDLE'; w.message='登录请求已提交，等待游戏状态识别'; w.last_heartbeat=timezone.now(); w.save(); self.log(a,'LOGIN_SUBMITTED','账号密码已提交，密码不会写入日志')
        except Exception as e:
            w.state='ERROR'; w.message=str(e); w.save(); self.log(a,'WORKER_ERROR',str(e),'ERROR')
manager=WorkerManager()
