from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Account,Worker,Log
from engine.manager import manager
from engine.monitor import monitor
from engine.task_runner import TaskRunner
from engine.window_manager import enumerate_windows


def dashboard(request):
    rows=[]
    for a in Account.objects.all().order_by('-id'):
        w=getattr(a,'worker',None)
        rows.append((a,w,Log.objects.filter(account=a).order_by('-id')[:10]))
    monitor.start()
    return render(request,'dashboard.html',{'rows':rows})


def add_account(request):
    if request.method=='POST':
        a=Account.objects.create(
            name=request.POST.get('name','未命名'),account_name=request.POST.get('account_name',''),
            password=request.POST.get('password',''),login_mode=request.POST.get('login_mode','password'),
            game_exe=request.POST.get('game_exe',''),window_title=request.POST.get('window_title','梦幻西游'),
            launch_args=request.POST.get('launch_args',''),auto_login=bool(request.POST.get('auto_login')),
            auto_reconnect=bool(request.POST.get('auto_reconnect')),auto_daily=bool(request.POST.get('auto_daily')))
        Worker.objects.create(account=a); Log.objects.create(account=a,event='ACCOUNT_CREATE',message='账号已添加')
        return redirect('/')
    return render(request,'add_account.html')


@require_POST
def start(request,pk):
    a=get_object_or_404(Account,pk=pk); manager.start(a); return redirect('/')


@require_POST
def stop(request,pk):
    a=get_object_or_404(Account,pk=pk); manager.stop(a); return redirect('/')


def logs(request,pk):
    a=get_object_or_404(Account,pk=pk); return render(request,'logs.html',{'account':a,'logs':Log.objects.filter(account=a).order_by('-id')[:300]})


def task(request,pk):
    if request.method=='POST':
        name=request.POST.get('task','daily')
        TaskRunner(dry_run=True).run_once(pk,name)
    return redirect('/')


def status(request):
    out=[]
    for a in Account.objects.all():
        w=getattr(a,'worker',None)
        out.append({'id':a.id,'name':a.name,'state':getattr(w,'state','STOPPED'),'task':getattr(w,'task','空闲'),'progress':getattr(w,'progress',0),'message':getattr(w,'message',''),'pid':getattr(w,'pid',None),'reconnects':getattr(w,'reconnects',0),'world':getattr(w,'world',''),'x':getattr(w,'position_x',None),'y':getattr(w,'position_y',None)})
    return JsonResponse(out,safe=False)


def windows(request):
    try:return JsonResponse([w.__dict__ for w in enumerate_windows()],safe=False)
    except Exception as e:return JsonResponse({'error':str(e)},status=500)
