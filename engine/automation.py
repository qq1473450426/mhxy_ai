import time
from pathlib import Path
import cv2,numpy as np
from PIL import ImageGrab
import pyautogui

class AutomationEngine:
    def __init__(self,dry_run=True,threshold=.88):self.dry_run=dry_run;self.threshold=threshold
    def capture(self,rect):
        if not rect:return None
        return cv2.cvtColor(np.array(ImageGrab.grab(bbox=rect)),cv2.COLOR_RGB2BGR)
    def find_template(self,frame,path,threshold=None):
        tpl=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
        if frame is None or tpl is None:return None
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);r=cv2.matchTemplate(gray,tpl,cv2.TM_CCOEFF_NORMED);_,score,_,loc=cv2.minMaxLoc(r);th=threshold or self.threshold
        if score<th:return None
        h,w=tpl.shape[:2];return {'x':loc[0]+w//2,'y':loc[1]+h//2,'score':float(score)}
    def click(self,x,y):
        if self.dry_run:return
        pyautogui.click(x,y)
    def press(self,key):
        if self.dry_run:return
        pyautogui.press(key)
    def wait(self,s):time.sleep(s)
