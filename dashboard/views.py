import json
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from engine.credential_store import encrypt_password
from engine.manager import manager
from engine.reconnect import ReconnectCoordinator, ReconnectPolicy
from engine.task_runner import TaskRunner
from engine.leveling import NewServerLevelingStrategy, candidates_from_mapping
from engine.perception import PerceptionConfig, ScreenLevelingObserver
from engine.window_manager import enumerate_windows
from engine.control import MultiOpenController, LayoutConfig
from .models import Account, GMTask, Log, Worker


def _body(request):
    try: return json.loads(request.body or '{}')
    except json.JSONDecodeError: return {}


def _account_data(account):
    worker = getattr(account, 'worker', None)
    return {
        'id': account.id, 'name': account.name, 'account_name': account.account_name, 'enabled': account.enabled,
        'window_title': account.window_title, 'state': getattr(worker, 'state', 'STOPPED'), 'task': getattr(worker, 'task', '空闲'),
        'progress': getattr(worker, 'progress', 0), 'message': getattr(worker, 'message', ''), 'world': getattr(worker, 'world', ''),
        'updated': getattr(worker, 'updated', None), 'has_password': bool(account.password), 'auto_login': account.auto_login,
        'auto_reconnect': account.auto_reconnect, 'auto_daily': account.auto_daily, 'max_reconnect_attempts': account.max_reconnect_attempts,
        'max_backup_switches': account.max_backup_switches, 'reconnect_delay_seconds': account.reconnect_delay_seconds,
        'backup_account_ids': list(account.backup_accounts.values_list('id', flat=True)), 'character_slot': account.character_slot,
        'role_name': account.role_name, 'team_priority': account.team_priority, 'is_team_leader': account.is_team_leader,
        'auto_story_skip': account.auto_story_skip, 'auto_battle': account.auto_battle, 'battle_template': account.battle_template,
        'equipment_policy': account.equipment_policy,
    }


def _task_data(task):
    return {'id': task.id, 'name': task.name, 'type': task.task_type, 'type_label': task.get_task_type_display(), 'status': task.status, 'status_label': task.get_status_display(), 'condition': task.condition, 'description': task.description, 'rewards': task.rewards, 'knowledge_key': task.knowledge_key, 'progress': task.progress, 'publisher': task.publisher, 'published_at': task.published_at, 'created': task.created, 'updated': task.updated}


@require_http_methods(['GET'])
def overview(request):
    task_rows = GMTask.objects.all(); counts = {row['status']: row['count'] for row in task_rows.values('status').annotate(count=Count('id'))}
    return JsonResponse({'counts': {'total': task_rows.count(), 'active': counts.get('ACTIVE', 0), 'pending': counts.get('PENDING', 0), 'done': counts.get('DONE', 0), 'cancelled': counts.get('CANCELLED', 0)}, 'type_counts': list(task_rows.values('task_type').annotate(count=Count('id')).order_by('task_type')), 'recent_logs': [{'id': x.id, 'level': x.level, 'event': x.event, 'message': x.message, 'created': x.created, 'account': x.account.name} for x in Log.objects.select_related('account').order_by('-created')[:6]], 'workers': [_account_data(a) for a in Account.objects.all().order_by('-updated')]})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def tasks(request):
    if request.method == 'GET':
        query, status, task_type = request.GET.get('q', '').strip(), request.GET.get('status', '').strip(), request.GET.get('type', '').strip(); rows = GMTask.objects.all()
        if query: rows = rows.filter(name__icontains=query)
        if status: rows = rows.filter(status=status)
        if task_type: rows = rows.filter(task_type=task_type)
        return JsonResponse({'results': [_task_data(x) for x in rows]})
    data = _body(request); task = GMTask.objects.create(name=data.get('name', '未命名任务').strip() or '未命名任务', task_type=data.get('type', 'DAILY'), status=data.get('status', 'DRAFT'), condition=data.get('condition', ''), description=data.get('description', ''), rewards=data.get('rewards', ''), knowledge_key=data.get('knowledge_key', ''), publisher=data.get('publisher', 'GM001'))
    if task.status == 'ACTIVE': task.published_at = timezone.now(); task.save(update_fields=['published_at', 'updated'])
    return JsonResponse(_task_data(task), status=201)


@csrf_exempt
@require_http_methods(['GET', 'PATCH', 'DELETE'])
def task_detail(request, pk):
    task = get_object_or_404(GMTask, pk=pk)
    if request.method == 'GET': return JsonResponse(_task_data(task))
    if request.method == 'DELETE': task.delete(); return JsonResponse({'ok': True})
    data = _body(request)
    for source, target in {'name': 'name', 'type': 'task_type', 'status': 'status', 'condition': 'condition', 'description': 'description', 'rewards': 'rewards', 'knowledge_key': 'knowledge_key', 'progress': 'progress', 'publisher': 'publisher'}.items():
        if source in data: setattr(task, target, data[source])
    if data.get('status') == 'ACTIVE' and not task.published_at: task.published_at = timezone.now()
    task.save(); return JsonResponse(_task_data(task))


@csrf_exempt
@require_http_methods(['POST'])
def task_action(request, pk):
    task = get_object_or_404(GMTask, pk=pk); action = _body(request).get('action'); states = {'submit': 'PENDING', 'approve': 'ACTIVE', 'complete': 'DONE', 'cancel': 'CANCELLED', 'draft': 'DRAFT'}
    if action not in states: return JsonResponse({'error': '未知操作'}, status=400)
    task.status = states[action]
    if task.status == 'ACTIVE' and not task.published_at: task.published_at = timezone.now()
    if task.status == 'DONE': task.progress = 100
    task.save(); return JsonResponse(_task_data(task))


@require_http_methods(['GET'])
def knowledge_search(request):
    # Knowledge/SkillStore is not part of the current engine.skills public API.
    # Keep this endpoint backward-compatible without making Django import fail.
    return JsonResponse({'results': []})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def leveling_strategy(request):
    strategy = NewServerLevelingStrategy()
    if request.method == 'GET':
        try: level, target = int(request.GET.get('level', 0)), int(request.GET.get('target_level', 69))
        except ValueError: return JsonResponse({'error': 'level/target_level 必须是整数'}, status=400)
        return JsonResponse({'level': level, 'target_level': target, 'stage': strategy.stage_for_level(level), 'priority': strategy.priority_order(level)})
    data = _body(request)
    try: level, target = int(data.get('level', 0)), int(data.get('target_level', 69))
    except (TypeError, ValueError): return JsonResponse({'error': 'level/target_level 必须是整数'}, status=400)
    decision = strategy.choose(level, candidates_from_mapping(data.get('candidates', [])), target_level=target, weights=data.get('weights'))
    return JsonResponse({'level': level, 'target_level': target, 'stage': decision.stage, 'task': decision.task, 'score': decision.score, 'reason': decision.reason})


@require_http_methods(['GET'])
def leveling_observe(request):
    try: account_id = int(request.GET.get('account_id', 0))
    except ValueError: return JsonResponse({'error': 'account_id 必须是整数'}, status=400)
    account = get_object_or_404(Account, pk=account_id); observer = ScreenLevelingObserver(hwnd=account.hwnd, window_title=account.window_title, config=PerceptionConfig(), dry_run=True)
    return JsonResponse(observer.observe())


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def accounts(request):
    if request.method == 'GET': return JsonResponse({'results': [_account_data(a) for a in Account.objects.all().order_by('-id')]})
    data = _body(request); account = Account.objects.create(
        name=data.get('name', '未命名账号').strip() or '未命名账号', account_name=data.get('account_name', '').strip(), password=encrypt_password(data.get('password', '')),
        login_mode=data.get('login_mode', 'password'), game_exe=data.get('game_exe', ''), window_title=data.get('window_title', '梦幻西游'), launch_args=data.get('launch_args', ''),
        auto_login=bool(data.get('auto_login', True)), auto_reconnect=bool(data.get('auto_reconnect', True)), auto_daily=bool(data.get('auto_daily', False)),
        max_reconnect_attempts=max(0, int(data.get('max_reconnect_attempts', 3))), max_backup_switches=max(0, int(data.get('max_backup_switches', 2))), reconnect_delay_seconds=max(1, int(data.get('reconnect_delay_seconds', 15))),
        character_slot=max(1, int(data.get('character_slot', 1))), role_name=data.get('role_name', ''), team_priority=max(0, int(data.get('team_priority', 0))), is_team_leader=bool(data.get('is_team_leader', False)),
        auto_story_skip=bool(data.get('auto_story_skip', True)), auto_battle=bool(data.get('auto_battle', True)), battle_template=data.get('battle_template', '普通任务战斗'), equipment_policy=data.get('equipment_policy', 'BEST_COMBAT'))
    Worker.objects.create(account=account); Log.objects.create(account=account, event='ACCOUNT_CREATE', message='账号已添加，密码已加密存储'); _set_backups(account, data.get('backup_account_ids', [])); return JsonResponse(_account_data(account), status=201)


def _set_backups(account, ids):
    valid = Account.objects.filter(id__in=[int(x) for x in ids if str(x).isdigit()]).exclude(id=account.id); account.backup_accounts.set(valid)


@csrf_exempt
@require_http_methods(['GET', 'PATCH', 'DELETE'])
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'GET': return JsonResponse(_account_data(account))
    if request.method == 'DELETE': account.delete(); return JsonResponse({'ok': True})
    data = _body(request)
    for key in ['name','account_name','login_mode','game_exe','window_title','launch_args','role_name','battle_template','equipment_policy']:
        if key in data: setattr(account, key, data[key])
    for key in ['enabled','auto_login','auto_reconnect','auto_daily','is_team_leader','auto_story_skip','auto_battle']:
        if key in data: setattr(account, key, bool(data[key]))
    for key in ['max_reconnect_attempts','max_backup_switches','reconnect_delay_seconds','character_slot','team_priority']:
        if key in data: setattr(account, key, max(0, int(data[key])))
    if data.get('password'): account.password = encrypt_password(data['password'])
    account.save()
    if 'backup_account_ids' in data: _set_backups(account, data['backup_account_ids'])
    Log.objects.create(account=account, event='ACCOUNT_UPDATE', message='账号配置已更新'); return JsonResponse(_account_data(account))


@csrf_exempt
@require_http_methods(['POST'])
def control_action(request):
    data = _body(request); action = data.get('action', 'start'); ids = [int(x) for x in data.get('account_ids', []) if str(x).isdigit()]; accounts_qs = Account.objects.filter(id__in=ids, enabled=True).order_by('team_priority', 'id')
    accounts = list(accounts_qs)
    controller = MultiOpenController()
    if action == 'start':
        mode = data.get('mode', 'single'); layout = LayoutConfig(columns=max(1, int(data.get('columns', 2))), width=max(320, int(data.get('width', 960))), height=max(240, int(data.get('height', 540))), gap=max(0, int(data.get('gap', 8))), origin_x=int(data.get('origin_x', 0)), origin_y=int(data.get('origin_y', 0)))
        result = controller.start(accounts, mode, layout)
        return JsonResponse({'result': result, 'roles': controller.role_plan(accounts)})
    if action == 'stop': return JsonResponse({'result': controller.stop(accounts)})
    if action == 'arrange': return JsonResponse({'result': controller.arrange(accounts, LayoutConfig())})
    if action == 'role_plan': return JsonResponse({'result': controller.role_plan(accounts, data.get('recommended_roles'))})
    return JsonResponse({'error': '未知控制动作'}, status=400)


class _ManagerReconnectExecutor:
    def reconnect(self, account_id, password=None):
        account = Account.objects.get(pk=account_id); manager.start(account); return {'success': True}
    def switch_account(self, failed_account_id, backup_account_id):
        failed = Account.objects.get(pk=failed_account_id); backup = Account.objects.get(pk=backup_account_id); manager.stop(failed); manager.start(backup); return {'success': True}


@csrf_exempt
@require_http_methods(['POST'])
def account_action(request, pk):
    account = get_object_or_404(Account, pk=pk); data = _body(request); action = data.get('action')
    if action == 'start': manager.start(account)
    elif action == 'stop': manager.stop(account)
    elif action == 'run_task': TaskRunner(dry_run=True).run_once(account.id, data.get('task', 'daily'))
    elif action == 'reconnect':
        backups = list(account.backup_accounts.values_list('id', flat=True)); state = type('State', (), {'account_id': account.id, 'attempts': 0, 'backup_switches': 0, 'active_account_id': None, 'failed': False, 'events': []})()
        coordinator = ReconnectCoordinator(_ManagerReconnectExecutor(), ReconnectPolicy(account.max_reconnect_attempts, account.max_backup_switches, account.reconnect_delay_seconds)); result = coordinator.handle_disconnect(state, backups)
        worker, _ = Worker.objects.get_or_create(account=account)
        if result['status'] in {'RECONNECTED', 'SWITCHED_BACKUP'}: worker.reconnects += 1; worker.state = 'STARTING'; worker.message = result['status']; worker.save(update_fields=['reconnects','state','message','updated'])
        Log.objects.create(account=account, event='RECONNECT', message=json.dumps(result, ensure_ascii=False)); return JsonResponse({'account': _account_data(account), 'result': result})
    else: return JsonResponse({'error': '未知操作'}, status=400)
    account.refresh_from_db(); return JsonResponse(_account_data(account))


@require_http_methods(['GET'])
def windows(request):
    try: return JsonResponse([w.__dict__ for w in enumerate_windows()], safe=False)
    except Exception as exc: return JsonResponse({'error': str(exc)}, status=500)
