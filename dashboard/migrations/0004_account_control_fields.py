from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('dashboard', '0003_account_security_reconnect')]

    operations = [
        migrations.AddField(model_name='account', name='character_slot', field=models.PositiveSmallIntegerField(default=1, help_text='默认角色槽位，1=第一个角色')),
        migrations.AddField(model_name='account', name='role_name', field=models.CharField(blank=True, help_text='角色/门派定位，如辅助、输出', max_length=40)),
        migrations.AddField(model_name='account', name='team_priority', field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name='account', name='is_team_leader', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='account', name='auto_story_skip', field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account', name='auto_battle', field=models.BooleanField(default=True)),
        migrations.AddField(model_name='account', name='battle_template', field=models.CharField(default='普通任务战斗', max_length=80)),
        migrations.AddField(model_name='account', name='equipment_policy', field=models.CharField(default='BEST_COMBAT', max_length=40)),
    ]
