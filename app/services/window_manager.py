from dataclasses import dataclass
import time
import win32gui,win32con
@dataclass
class WindowInfo:
    hwnd:int; title:str; left:int; top:int; right:int; bottom:int
    @property
    def width(self):return self.right-self.left
    @property
    def height(self):return self.bottom-self.top
class WindowManager:
    def enumerate_windows(self):
        out=[]
        def cb(hwnd,_):
            if not win32gui.IsWindowVisible(hwnd):return
            title=win32gui.GetWindowText(hwnd).strip()
            if not title:return
            try:r=win32gui.GetWindowRect(hwnd)
            except Exception:return
            out.append(WindowInfo(hwnd,title,*r))
        win32gui.EnumWindows(cb,None);return out
    def find_by_title(self,title):
        if not title:return None
        for w in self.enumerate_windows():
            if title.lower() in w.title.lower():return w
        return None
    def get_info(self,hwnd=None,title=None):
        if hwnd and win32gui.IsWindow(hwnd):return WindowInfo(hwnd,win32gui.GetWindowText(hwnd),*win32gui.GetWindowRect(hwnd))
        return self.find_by_title(title)
    def activate(self,hwnd):
        if not hwnd or not win32gui.IsWindow(hwnd):return False
        try:win32gui.ShowWindow(hwnd,win32con.SW_RESTORE);win32gui.SetForegroundWindow(hwnd);time.sleep(.1);return True
        except Exception:return False
