import time,pyautogui
class InputController:
    def __init__(self,dry_run=True):self.dry_run=dry_run
    def move_click(self,x,y):
        if self.dry_run:return {'ok':True,'dry_run':True,'action':'click','x':x,'y':y}
        pyautogui.moveTo(x,y,duration=.08);pyautogui.click();return {'ok':True}
    def press(self,key):
        if self.dry_run:return {'ok':True,'dry_run':True,'action':'press','key':key}
        pyautogui.press(key);time.sleep(.05);return {'ok':True}
