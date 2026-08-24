import asyncio,json
from pathlib import Path
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.logging_setup import get_logger
from app.services.database import Database
from app.services.window_manager import WindowManager
from app.services.capture import CaptureService
from app.services.vision import VisionService
from app.services.input_controller import InputController
from app.services.scheduler import Scheduler
from app.services.monitor import Monitor
from app.services.knowledge import KnowledgeService
from app.workers.worker import Worker
BASE=Path(__file__).resolve().parents[2];SETTINGS=json.loads((BASE/'config/config.json').read_text(encoding='utf-8'));ACCOUNTS=json.loads((BASE/'config/accounts.json').read_text(encoding='utf-8'))
app=FastAPI(title='MHXY AI Multi Account Controller');app.mount('/static',StaticFiles(directory=BASE/'static'),name='static');templates=Jinja2Templates(directory=BASE/'templates')
logger=get_logger('controller');db=Database();window_manager=WindowManager();capture=CaptureService();vision=VisionService(SETTINGS['template_threshold']);input_controller=InputController(SETTINGS['dry_run']);scheduler=Scheduler();knowledge=KnowledgeService();workers={};monitor=None;monitor_task=None
class Controller:
 def __init__(self):self.workers=workers;self.db=db;self.settings=SETTINGS;self.window_manager=window_manager;self.capture=capture;self.vision=vision;self.input=input_controller;self.scheduler=scheduler;self.knowledge=knowledge
 async def recover_worker(self,w):
  from app.services.reconnect import ReconnectManager
  try:
   if w.status.state==w.status.state.ERROR:w.status.state=w.status.state.DISCONNECTED
   if w.status.state==w.status.state.DISCONNECTED:w.status.state=w.status.state.RECONNECTING
   ok=await ReconnectManager(w,SETTINGS['max_reconnect_attempts'],SETTINGS['reconnect_interval']).run()
   if ok:w.status.state=w.status.state.LOGIN;await asyncio.sleep(1);w.status.state=w.status.state.IDLE;w.controller.db.state(w.status);return
   w.status.state=w.status.state.MANUAL_REQUIRED;w.controller.db.state(w.status);r=scheduler.idle_replacement(w.account_id)
   if r and w.task_name:r.set_task(w.task_name);r.start();w.log('WARN','AUTO_SWITCH',f'切换到备用账号 {r.account_id}')
  except Exception as e:w.log('ERROR','RECOVERY_EXCEPTION',repr(e))
controller=Controller()
@app.on_event('startup')
async def startup():
 global monitor,monitor_task
 for a in ACCOUNTS:
  if a.get('enabled',True):
   w=Worker(a,controller);workers[w.account_id]=w;scheduler.register(w)
 monitor=Monitor(controller);monitor_task=asyncio.create_task(monitor.run());logger.info('主控板启动：Worker=%s dry_run=%s',len(workers),SETTINGS['dry_run'])
@app.on_event('shutdown')
async def shutdown():
 if monitor:monitor.stop()
 if monitor_task:monitor_task.cancel()
 for w in workers.values():await w.stop()
@app.get('/',response_class=HTMLResponse)
async def index(request:Request):return templates.TemplateResponse('index.html',{'request':request,'dry_run':SETTINGS['dry_run']})
@app.get('/api/status')
async def status():return {'dry_run':SETTINGS['dry_run'],'workers':[w.snapshot() for w in workers.values()],'knowledge_available':knowledge.available()}
@app.get('/api/windows')
async def windows():return [w.__dict__|{'width':w.width,'height':w.height} for w in window_manager.enumerate_windows()]
@app.get('/api/logs')
async def logs(limit:int=200):return JSONResponse(db.recent_events(max(1,min(500,limit))))
@app.post('/api/account/{aid}/start')
async def start(aid):
 w=workers.get(aid)
 if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
 w.start();return {'ok':True}
@app.post('/api/account/{aid}/stop')
async def stop(aid):
 w=workers.get(aid)
 if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
 await w.stop();return {'ok':True}
@app.post('/api/account/{aid}/task')
async def task(aid,request:Request):
 w=workers.get(aid)
 if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
 d=await request.json();w.set_task(d['task_name']);w.start() if not w.running else None;return {'ok':True}
@app.post('/api/account/{aid}/screenshot')
async def screenshot(aid):
 w=workers.get(aid)
 if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
 p=w.save_screenshot('manual');return {'ok':bool(p),'path':p}
@app.post('/api/account/{aid}/simulate-disconnect')
async def sim(aid):
 w=workers.get(aid)
 if not w:return JSONResponse({'ok':False,'error':'账号不存在'},404)
 w.handle_disconnect('Web 控制台模拟掉线');return {'ok':True}
@app.post('/api/shutdown-all')
async def shutdown_all():
 for w in workers.values():await w.stop()
 return {'ok':True}
@app.get('/api/knowledge/search')
async def knowledge_search(q:str):return {'query':q,'results':knowledge.search(q)}
