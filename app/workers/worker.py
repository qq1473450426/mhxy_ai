import asyncio,time
from app.core.models import WorkerStatus,WorkerState
from app.core.logging_setup import get_logger
from app.core.state_machine import transition
from app.services.ai import LocalReasoningEngine
class Worker:
 def __init__(self,a,controller):
  self.controller=controller;self.account_id=a['account_id'];self.name=a['name'];self.hwnd=a.get('hwnd');self.window_title=a.get('window_title','');self.priority=int(a.get('priority',0));self.status=WorkerStatus(self.account_id);self.logger=get_logger('worker',self.account_id);self.running=False;self.task_handle=None;self.task_name=None;self._last_frame_signature=None;self.reasoning=LocalReasoningEngine()
 def log(self,level,event,message):
  text=f'ACCOUNT={self.account_id} | STATE={self.status.state.value} | EVENT={event} | {message}';getattr(self.logger,'error' if level=='ERROR' else 'warning' if level=='WARN' else 'info')(text);self.controller.db.event(self.account_id,level,event,message)
 def change_state(self,t):self.status.state=transition(self.status.state,t);self.controller.db.state(self.status);self.log('INFO','STATE_CHANGE',f'-> {t.value}')
 def heartbeat(self):self.status.last_heartbeat=time.time();self.controller.db.state(self.status)
 def window_info(self):return self.controller.window_manager.get_info(hwnd=self.hwnd,title=self.window_title)
 def window_exists(self):return self.window_info() is not None
 def activate_window(self):
  w=self.window_info();return self.controller.window_manager.activate(w.hwnd) if w else False
 def is_available_for_replacement(self):return self.status.state in {WorkerState.STOPPED,WorkerState.IDLE}
 def start(self):
  if self.running:return
  self.running=True;self.status.error_message=''
  try:self.change_state(WorkerState.STARTING)
  except ValueError:self.status.state=WorkerState.STARTING
  self.task_handle=asyncio.create_task(self.run())
 async def stop(self):
  self.running=False
  if self.task_handle:self.task_handle.cancel()
  self.status.state=WorkerState.STOPPED;self.controller.db.state(self.status);self.log('INFO','STOP','Worker 已停止')
 def set_task(self,n):self.task_name=n;self.status.task_name=n;self.log('INFO','TASK_ASSIGN',f'任务={n}')
 async def run(self):
  try:
   if not self.window_exists():self.mark_error('未找到游戏窗口');return
   self.change_state(WorkerState.LOGIN);await asyncio.sleep(1);self.change_state(WorkerState.IDLE)
   while self.running:
    self.heartbeat()
    if not self.task_name:await asyncio.sleep(1);continue
    if self.status.state==WorkerState.IDLE:self.change_state(WorkerState.RUNNING)
    d=self.reasoning.decide(self.account_id,self.build_observation(),{'task_name':self.task_name});self.status.last_ai_action=d.action;self.log('INFO','LOCAL_AI_DECISION',f'action={d.action} confidence={d.confidence:.2f} reason={d.reason}')
    if d.action=='RECONNECT':self.handle_disconnect('本地推理判断需要重连')
    elif d.action=='TASK_COMPLETE':self.log('INFO','TASK_COMPLETE',self.task_name);self.task_name=None;self.status.task_name='空闲'
    elif d.action=='WAIT':await asyncio.sleep(.5)
    else:await self.execute_task(self.task_name)
  except asyncio.CancelledError:pass
  except Exception as e:self.status.error_message=repr(e);self.status.state=WorkerState.ERROR;self.controller.db.state(self.status);self.log('ERROR','WORKER_EXCEPTION',repr(e))
 def build_observation(self):
  info=self.window_info();connected=info is not None;frame=self.capture() if connected else None
  def found(n):
   try:return bool(self.controller.vision.find(frame,n,self.controller.settings['template_threshold']))
   except FileNotFoundError:return False
  battle=found('battle_attack.png');return {'state':self.status.state.value,'connected':connected,'battle_detected':battle,'dialog_detected':found('dialog.png'),'target_found':battle,'task_done':found('battle_end.png'),'confidence':.9 if connected else .1}
 async def execute_task(self,name):
  from app.services.task_runner import TaskRunner
  try:await asyncio.to_thread(TaskRunner(self).run_task,name)
  except FileNotFoundError as e:self.log('ERROR','TASK_NOT_FOUND',str(e));self.task_name=None
  except Exception as e:self.log('ERROR','TASK_ERROR',repr(e));self.handle_disconnect('任务异常')
  await asyncio.sleep(.2)
 def capture(self):
  frame=self.controller.capture.capture_window(self.window_info())
  if frame is not None:
   import cv2
   sig=cv2.resize(frame,(32,18)).mean(axis=(0,1)).tolist()
   if self._last_frame_signature is None or sum(abs(a-b) for a,b in zip(sig,self._last_frame_signature))>3:self.status.last_screen_change=time.time();self._last_frame_signature=sig
  return frame
 def save_screenshot(self,reason):
  p=self.controller.capture.save(self.capture(),self.account_id,reason)
  if p:self.log('INFO','SCREENSHOT',p)
  return p
 def find_click(self,t,confidence,timeout):
  end=time.time()+timeout
  while time.time()<end and self.running:
   m=self.controller.vision.find(self.capture(),t,confidence)
   if m:
    w=self.window_info()
    if not w:return False
    x,y=w.left+m['x'],w.top+m['y'];self.log('INFO','TEMPLATE_MATCH',f'{t} confidence={m["confidence"]:.3f} screen=({x},{y})')
    if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_CLICK',f'({x},{y})');return True
    return self.controller.input.move_click(x,y)['ok']
   time.sleep(.15)
  self.log('WARN','TEMPLATE_TIMEOUT',f'template={t}');return False
 def click_client(self,x,y):
  w=self.window_info()
  if not w:return False
  if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_CLICK',f'client=({x},{y})');return True
  return self.controller.input.move_click(w.left+x,w.top+y)['ok']
 def press_key(self,key):
  if self.controller.settings['dry_run']:self.log('INFO','DRY_RUN_KEY',key);return True
  return self.controller.input.press(key)['ok']
 def handle_disconnect(self,reason):
  self.status.error_message=reason
  try:
   if self.status.state not in {WorkerState.DISCONNECTED,WorkerState.RECONNECTING,WorkerState.MANUAL_REQUIRED}:self.change_state(WorkerState.DISCONNECTED)
  except ValueError:self.status.state=WorkerState.DISCONNECTED
  self.save_screenshot('disconnect');self.log('WARN','DISCONNECTED',reason)
 def mark_error(self,msg):
  self.status.error_message=msg
  try:self.change_state(WorkerState.ERROR)
  except ValueError:self.status.state=WorkerState.ERROR
  self.save_screenshot('error');self.log('ERROR','ERROR',msg)
 def is_idle(self):return self.status.state==WorkerState.IDLE
 def snapshot(self):
  w=self.window_info();return {'account_id':self.account_id,'name':self.name,'state':self.status.state.value,'task_name':self.status.task_name,'running':self.running,'hwnd':w.hwnd if w else None,'last_heartbeat':self.status.last_heartbeat,'last_screen_change':self.status.last_screen_change,'reconnect_count':self.status.reconnect_count,'action_count':self.status.action_count,'error_message':self.status.error_message}
