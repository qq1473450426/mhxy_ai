import json,time
from pathlib import Path
class TaskRunner:
    def __init__(self,worker):self.worker=worker
    def load(self,name):
        p=Path('tasks')/f'{name}.json'
        if not p.exists():raise FileNotFoundError(f'任务不存在：{p}')
        return json.loads(p.read_text(encoding='utf-8'))
    def run_step(self,s):
        t=s.get('type')
        if t=='wait':time.sleep(float(s.get('seconds',1)));return True
        if t=='key':return self.worker.press_key(s['key'])
        if t=='click':return self.worker.click_client(int(s['x']),int(s['y']))
        if t=='find_click':return self.worker.find_click(s['template'],float(s.get('confidence',.88)),float(s.get('timeout',5)))
        if t=='screenshot':self.worker.save_screenshot(s.get('reason','manual'));return True
        raise ValueError(f'未知任务动作：{t}')
    def run_task(self,name):
        task=self.load(name)
        while self.worker.running:
            for i,s in enumerate(task.get('steps',[]),1):
                if not self.worker.running:return
                self.worker.log('INFO','TASK_STEP',f'{name} step={i} type={s.get("type")}');self.run_step(s)
            if not task.get('loop',False):return
