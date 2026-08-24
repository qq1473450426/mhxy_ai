from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
 initial=True; dependencies=[]
 operations=[
  migrations.CreateModel(name='Account',fields=[('id',models.BigAutoField(primary_key=True,serialize=False)),('name',models.CharField(max_length=80)),('account_name',models.CharField(blank=True,max_length=120)),('password',models.TextField(blank=True)),('login_mode',models.CharField(default='password',max_length=20)),('game_exe',models.CharField(blank=True,max_length=500)),('window_title',models.CharField(default='梦幻西游',max_length=200)),('enabled',models.BooleanField(default=True))]),
  migrations.CreateModel(name='Worker',fields=[('id',models.BigAutoField(primary_key=True,serialize=False)),('state',models.CharField(default='STOPPED',max_length=30)),('task',models.CharField(default='空闲',max_length=120)),('progress',models.PositiveIntegerField(default=0)),('message',models.CharField(blank=True,max_length=500)),('reconnects',models.PositiveIntegerField(default=0)),('updated',models.DateTimeField(auto_now=True)),('account',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='worker',to='dashboard.account'))]),
  migrations.CreateModel(name='Log',fields=[('id',models.BigAutoField(primary_key=True,serialize=False)),('level',models.CharField(default='INFO',max_length=10)),('event',models.CharField(max_length=80)),('message',models.TextField()),('created',models.DateTimeField(auto_now_add=True)),('account',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='logs',to='dashboard.account'))])
 ]
