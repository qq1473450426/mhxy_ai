from django.db import models
class Account(models.Model):
    name=models.CharField(max_length=80)
    account_name=models.CharField(max_length=120,blank=True)
    password=models.TextField(blank=True)
    login_mode=models.CharField(max_length=20,default='password')
    game_exe=models.CharField(max_length=500,blank=True)
    window_title=models.CharField(max_length=200,default='梦幻西游')
    enabled=models.BooleanField(default=True)
    def __str__(self): return self.name
class Worker(models.Model):
    account=models.OneToOneField(Account,on_delete=models.CASCADE,related_name='worker')
    state=models.CharField(max_length=30,default='STOPPED')
    task=models.CharField(max_length=120,default='空闲')
    progress=models.PositiveIntegerField(default=0)
    message=models.CharField(max_length=500,blank=True)
    reconnects=models.PositiveIntegerField(default=0)
    updated=models.DateTimeField(auto_now=True)
class Log(models.Model):
    account=models.ForeignKey(Account,on_delete=models.CASCADE,related_name='logs')
    level=models.CharField(max_length=10,default='INFO')
    event=models.CharField(max_length=80)
    message=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
