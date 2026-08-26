from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('dashboard', '0001_initial')]

    operations = [
        migrations.AddField(model_name='account', name='hwnd', field=models.PositiveBigIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='account', name='launch_args', field=models.TextField(blank=True)),
        migrations.AddField(model_name='account', name='auto_login', field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account', name='auto_reconnect', field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account', name='auto_daily', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='account', name='max_reconnect_attempts', field=models.PositiveSmallIntegerField(default=3)),
        migrations.AddField(model_name='account', name='max_backup_switches', field=models.PositiveSmallIntegerField(default=2)),
        migrations.AddField(model_name='account', name='reconnect_delay_seconds', field=models.PositiveIntegerField(default=15)),
        migrations.AddField(model_name='account', name='backup_accounts', field=models.ManyToManyField(blank=True, related_name='backup_for_accounts', to='dashboard.account')),
        migrations.AddField(model_name='worker', name='pid', field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='worker', name='world', field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name='worker', name='position_x', field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name='worker', name='position_y', field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name='worker', name='current_action', field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name='worker', name='last_heartbeat', field=models.DateTimeField(blank=True, null=True)),
        migrations.AlterField(model_name='account', name='password', field=models.TextField(blank=True, help_text='Fernet 密文，禁止保存明文')),
    ]
