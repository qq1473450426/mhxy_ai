from pathlib import Path
import cv2
class VisionService:
    def __init__(self,threshold=.88):self.threshold=threshold;self.cache={}
    def _load(self,t):
        p=Path('assets/templates')/t
        if t not in self.cache:
            image=cv2.imread(str(p))
            if image is None:raise FileNotFoundError(f'模板不存在：{p}')
            self.cache[t]=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        return self.cache[t]
    def find(self,frame,t,threshold=None):
        if frame is None:return None
        tpl=self._load(t);gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        if gray.shape[0]<tpl.shape[0] or gray.shape[1]<tpl.shape[1]:return None
        r=cv2.matchTemplate(gray,tpl,cv2.TM_CCOEFF_NORMED);_,v,_,loc=cv2.minMaxLoc(r);limit=self.threshold if threshold is None else threshold
        if v<limit:return None
        h,w=tpl.shape[:2];return {'confidence':float(v),'x':int(loc[0]+w/2),'y':int(loc[1]+h/2),'w':w,'h':h}
