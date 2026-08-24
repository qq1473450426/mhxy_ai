from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from .models import Account,Worker,Log
import subprocess,os

def dashboard(request):
    rows=[]
    for a in Account.objects.all():
        w=getattr(a,'worker',None); rows.append((a,w,Log.objects.filter(account=a).order_by('-id')[:8]))
    return render(request,'dashboard.html',{'rows':rows})

def add_account(request):
    if request.method=='POST':
        a=Account.objects.create(name=request.POST.get('name','未命名'),account_name=request.POST.get('account_name',''),password=request.POST.get('password',''),login_mode=request.POST.get('login_mode','password'),game_exe=request.POST.get('game_exe',''),window_title=request.POST.get('window_title','梦幻西游'))
        Worker.objects.create(account=a); Log.objects.create(account=a,event='ACCOUNT_CREATE',message='账号已添加')
        return redirect('/')
    return render(request,'add_account.html')

def start(request,pk):
    a=get_object_or_404(Account,pk=pk); w,_=Worker.objects.get_or_create(account=a); w.state='LOGIN';w.message='准备启动客户端';w.save();Log.objects.create(account=a,event='START',message='收到启动指令')
    if a.game_exe and os.path.exists(a.game_exe): subprocess.Popen([a.game_exe])
    return redirect('/')

def stop(request,pk):
    a=get_object_or_404(Account,pk=pk);w,_=Worker.objects.get_or_create(account=a);w.state='STOPPED';w.message='已停止';w.save();Log.objects.create(account=a,event='STOP',message='已停止');return redirect('/')

def logs(request,pk):
    a=get_object_or_404(Account,pk=pk);return render(request,'logs.html',{'account':a,'logs':Log.objects.filter(account=a).order_by('-id')[:300]})

def status(request):
    return JsonResponse([{'id':a.id,'name':a.name,'state':getattr(getattr(a,'worker',None),'state','STOPPED'),'task':getattr(getattr(a,'worker',None),'task','空闲'),'progress':getattr(getattr(a,'worker',None),'progress',0),'message':getattr(getattr(a,'worker',None),'message','')} for a in Account.objects.all()],safe=False)

def windows(request):
    try:
        import win32gui
        out=[]
        def cb(h,_):
            t=win32gui.GetWindowText(h).strip()
            if t and win32gui.IsWindowVisible(h): out.append({'hwnd':h,'title':t})
        win32gui.EnumWindows(cb,None);return JsonResponse(out,safe=False)
    except Exception as e:return JsonResponse({'error':str(e)},status=500)
