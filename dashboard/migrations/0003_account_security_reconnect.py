from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('dashboard', '0002_v2')]

    operations = [
        migrations.AddField(model_name='account', name='max_reconnect_attempts', field=models.PositiveSmallIntegerField(default=3)),
        migrations.AddField(model_name='account', name='max_backup_switches', field=models.PositiveSmallIntegerField(default=2)),
        migrations.AddField(model_name='account', name='reconnect_delay_seconds', field=models.PositiveIntegerField(default=15)),
        migrations.AddField(model_name='account', name='backup_accounts', field=models.ManyToManyField(blank=True, related_name='backup_for_accounts', to='dashboard.account')),
        migrations.AlterField(model_name='account', name='password', field=models.TextField(blank=True, help_text='Fernet 密文，禁止保存明文')),
    ]
