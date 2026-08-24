from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('dashboard','0001_initial')]
    operations=[
        migrations.AddField(model_name='account',name='hwnd',field=models.PositiveBigIntegerField(blank=True,null=True)),
        migrations.AddField(model_name='account',name='launch_args',field=models.TextField(blank=True)),
        migrations.AddField(model_name='account',name='auto_login',field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account',name='auto_reconnect',field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account',name='auto_daily',field=models.BooleanField(default=False)),
        migrations.AddField(model_name='account',name='created',field=models.DateTimeField(auto_now_add=True,null=True)),
        migrations.AddField(model_name='account',name='updated',field=models.DateTimeField(auto_now=True,null=True)),
        migrations.AddField(model_name='worker',name='pid',field=models.PositiveIntegerField(blank=True,null=True)),
        migrations.AddField(model_name='worker',name='world',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='worker',name='position_x',field=models.IntegerField(blank=True,null=True)),
        migrations.AddField(model_name='worker',name='position_y',field=models.IntegerField(blank=True,null=True)),
        migrations.AddField(model_name='worker',name='current_action',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='worker',name='last_heartbeat',field=models.DateTimeField(blank=True,null=True)),
    ]
