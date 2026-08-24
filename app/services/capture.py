from pathlib import Path
import time,cv2,numpy as np
from PIL import ImageGrab
class CaptureService:
    def capture_window(self,w):
        if not w:return None
        img=ImageGrab.grab(bbox=(w.left,w.top,w.right,w.bottom))
        return cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
    def save(self,frame,account_id,reason):
        if frame is None:return None
        root=Path('screenshots')/account_id;root.mkdir(parents=True,exist_ok=True)
        p=root/f'{int(time.time())}_{reason}.png';cv2.imwrite(str(p),frame);return str(p)
