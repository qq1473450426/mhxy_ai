"""多开账号 API：CRUD、加密密码、备用账号、控制、登录与健康重连。"""
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from engine.credential_store import encrypt_password
from engine.login import login_account
from engine.manager import manager
from engine.multibox_monitor import monitor
from engine.task_runner import TaskRunner
from engine.control import MultiOpenController, LayoutConfig
from .models import Account, Log, Worker

def body(request):
    try: return json.loads(request.body or '{}')
    except json.JSONDecodeError: return {}

def data(account):
    worker=getattr(account,'worker',None)
    return {'id':account.id,'name':account.name,'account_name':account.account_name,'enabled':account.enabled,'game_exe':account.game_exe,'launch_args':account.launch_args,'window_title':account.window_title,'state':getattr(worker,'state','STOPPED'),'task':getattr(worker,'task','空闲'),'progress':getattr(worker,'progress',0),'message':getattr(worker,'message',''),'world':getattr(worker,'world',''),'updated':getattr(worker,'updated',None),'has_password':bool(account.password),'auto_login':account.auto_login,'auto_reconnect':account.auto_reconnect,'auto_daily':account.auto_daily,'max_reconnect_attempts':account.max_reconnect_attempts,'max_backup_switches':account.max_backup_switches,'reconnect_delay_seconds':account.reconnect_delay_seconds,'backup_account_ids':list(account.backup_accounts.values_list('id',flat=True)),'character_slot':account.character_slot,'role_name':account.role_name,'team_priority':account.team_priority,'is_team_leader':account.is_team_leader,'auto_story_skip':account.auto_story_skip,'auto_battle':account.auto_battle,'battle_template':account.battle_template,'equipment_policy':account.equipment_policy}

def set_backups(account,ids): account.backup_accounts.set(Account.objects.filter(id__in=[int(x) for x in ids if str(x).isdigit()]).exclude(id=account.id))

def assign(account,d):
    for k in ['role_name','battle_template','equipment_policy']:
        if k in d:setattr(account,k,d[k])
    for k in ['character_slot','team_priority']:
        if k in d:setattr(account,k,max(0,int(d[k])))
    for k in ['is_team_leader','auto_story_skip','auto_battle']:
        if k in d:setattr(account,k,bool(d[k]))

@csrf_exempt
@require_http_methods(['GET','POST'])
def accounts(request):
    if request.method=='GET':return JsonResponse({'results':[data(a) for a in Account.objects.all().order_by('team_priority','id')]})
    d=body(request)
    try: attempts,switches,delay=max(0,int(d.get('max_reconnect_attempts',3))),max(0,int(d.get('max_backup_switches',2))),max(1,int(d.get('reconnect_delay_seconds',15)))
    except (TypeError,ValueError):return JsonResponse({'error':'重连参数必须是数字'},status=400)
    a=Account.objects.create(name=d.get('name','未命名账号').strip() or '未命名账号',account_name=d.get('account_name','').strip(),password=encrypt_password(d.get('password','')),login_mode=d.get('login_mode','password'),game_exe=d.get('game_exe',''),window_title=d.get('window_title','梦幻西游'),launch_args=d.get('launch_args',''),auto_login=bool(d.get('auto_login',True)),auto_reconnect=bool(d.get('auto_reconnect',True)),auto_daily=bool(d.get('auto_daily',False)),max_reconnect_attempts=attempts,max_backup_switches=switches,reconnect_delay_seconds=delay)
    assign(a,d);a.save();Worker.objects.create(account=a);set_backups(a,d.get('backup_account_ids',[]));Log.objects.create(account=a,event='ACCOUNT_CREATE',message='账号已添加，密码已加密存储');return JsonResponse(data(a),status=201)

@csrf_exempt
@require_http_methods(['GET','PATCH','DELETE'])
def account_detail(request,pk):
    a=get_object_or_404(Account,pk=pk)
    if request.method=='GET':return JsonResponse(data(a))
    if request.method=='DELETE':a.delete();return JsonResponse({'ok':True})
    d=body(request)
    for k in ['name','account_name','login_mode','game_exe','window_title','launch_args','role_name','battle_template','equipment_policy']:
        if k in d:setattr(a,k,d[k])
    for k in ['enabled','auto_login','auto_reconnect','auto_daily','is_team_leader','auto_story_skip','auto_battle']:
        if k in d:setattr(a,k,bool(d[k]))
    for k in ['max_reconnect_attempts','max_backup_switches','reconnect_delay_seconds','character_slot','team_priority']:
        if k in d:setattr(a,k,max(0,int(d[k])))
    if d.get('password'):a.password=encrypt_password(d['password'])
    a.save()
    if 'backup_account_ids' in d:set_backups(a,d['backup_account_ids'])
    Log.objects.create(account=a,event='ACCOUNT_UPDATE',message='账号配置已更新');return JsonResponse(data(a))

@csrf_exempt
@require_http_methods(['POST'])
def control(request):
    d=body(request);ids=[int(x) for x in d.get('account_ids',[]) if str(x).isdigit()];accounts=list(Account.objects.filter(id__in=ids,enabled=True).order_by('team_priority','id'));action=d.get('action','start');controller=MultiOpenController()
    if action=='start':
        layout=LayoutConfig(columns=max(1,int(d.get('columns',2))),width=max(320,int(d.get('width',960))),height=max(240,int(d.get('height',540))),gap=max(0,int(d.get('gap',8))),origin_x=int(d.get('origin_x',0)),origin_y=int(d.get('origin_y',0)))
        return JsonResponse({'result':controller.start(accounts,d.get('mode','single'),layout),'roles':controller.role_plan(accounts,d.get('recommended_roles'))})
    if action=='stop':return JsonResponse({'result':controller.stop(accounts)})
    if action=='arrange':return JsonResponse({'result':controller.arrange(accounts,LayoutConfig())})
    if action=='role_plan':return JsonResponse({'result':controller.role_plan(accounts,d.get('recommended_roles'))})
    return JsonResponse({'error':'未知控制动作'},status=400)

@csrf_exempt
@require_http_methods(['POST'])
def account_action(request,pk):
    a=get_object_or_404(Account,pk=pk);action=body(request).get('action')
    if action=='start':manager.start(a)
    elif action=='stop':manager.stop(a)
    elif action=='login':
        result=login_account(a);Log.objects.create(account=a,event='LOGIN_MANUAL',message=f"登录执行：{result.get('status','UNKNOWN')}",level='INFO' if result.get('success') else 'WARN');return JsonResponse({'account':data(a),'result':{k:v for k,v in result.items() if k not in {'password','secret'}}})
    elif action=='run_task':TaskRunner(dry_run=True).run_once(a.id,body(request).get('task','daily'))
    elif action=='reconnect':return JsonResponse({'account':data(a),'result':monitor.check_account(a)})
    else:return JsonResponse({'error':'未知操作'},status=400)
    a.refresh_from_db();return JsonResponse(data(a))

@csrf_exempt
@require_http_methods(['POST'])
def multibox_health(request):
    d=body(request);ids=d.get('account_ids')
    if ids is None:ids=list(Account.objects.filter(enabled=True).values_list('id',flat=True))
    try:ids=[int(x) for x in ids]
    except (TypeError,ValueError):return JsonResponse({'error':'account_ids 必须是整数数组'},status=400)
    result=monitor.check_team(ids);return JsonResponse({'status':result.status,'accounts':result.accounts})
