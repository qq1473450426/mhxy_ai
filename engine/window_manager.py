from dataclasses import dataclass
import subprocess
import win32gui
import win32process

@dataclass
class WindowInfo:
    hwnd:int; title:str; pid:int; rect:tuple

def enumerate_windows():
    out=[]
    def cb(hwnd,_):
        if not win32gui.IsWindowVisible(hwnd): return
        title=win32gui.GetWindowText(hwnd).strip()
        if not title:return
        try:
            _,pid=win32process.GetWindowThreadProcessId(hwnd);out.append(WindowInfo(hwnd,title,pid,win32gui.GetWindowRect(hwnd)))
        except Exception:pass
    win32gui.EnumWindows(cb,None);return out

def find_window(hwnd=None,title=''):
    if hwnd and win32gui.IsWindow(hwnd):
        _,pid=win32process.GetWindowThreadProcessId(hwnd);return WindowInfo(hwnd,win32gui.GetWindowText(hwnd),pid,win32gui.GetWindowRect(hwnd))
    q=title.lower().strip()
    for w in enumerate_windows():
        if q and q in w.title.lower():return w
    return None

def launch_game(exe,args=''):
    if not exe: raise ValueError('未配置游戏客户端路径')
    return subprocess.Popen([exe]+([x for x in args.split() if x] if args else []))
