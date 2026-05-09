from django.db import migrations, models
from django.db.models import deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='home',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='home',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='home',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
        ),
        migrations.CreateModel(
            name='HomeMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member'), ('viewer', 'Viewer')], default='member', max_length=20)),
                ('can_manage_devices', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('home', models.ForeignKey(on_delete=deletion.CASCADE, related_name='memberships', to='devices.home')),
                ('user', models.ForeignKey(on_delete=deletion.CASCADE, related_name='home_memberships', to='auth.user')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('home', 'user'), name='unique_home_member'),
                ],
            },
        ),
        migrations.AddField(
            model_name='device',
            name='status',
            field=models.CharField(choices=[('unknown', 'Unknown'), ('online', 'Online'), ('offline', 'Offline')], default='unknown', max_length=20),
        ),
        migrations.AddField(
            model_name='device',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='device',
            name='state_payload',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='device',
            name='certificate_fingerprint',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='device',
            name='last_seen_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='device',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='metric_name',
            field=models.CharField(default='value', max_length=50),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='unit',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='payload',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='source',
            field=models.CharField(default='mq', max_length=30),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='device',
            field=models.ForeignKey(on_delete=deletion.CASCADE, related_name='readings', to='devices.device'),
        ),
        migrations.AddField(
            model_name='deviceaction',
            name='payload',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='deviceaction',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('acked', 'Acked'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='deviceaction',
            name='correlation_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='deviceaction',
            name='source',
            field=models.CharField(default='api', max_length=30),
        ),
        migrations.AlterField(
            model_name='deviceaction',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=deletion.SET_NULL, related_name='device_actions', to='auth.user'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['home', 'device_type'], name='devices_dev_home_id_948659_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['hardware_id'], name='devices_dev_hardwar_afffa3_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['status'], name='devices_dev_status_bbf58f_idx'),
        ),
        migrations.AddIndex(
            model_name='deviceaction',
            index=models.Index(fields=['device', '-timestamp'], name='devices_dev_device__dffea6_idx'),
        ),
        migrations.AddIndex(
            model_name='deviceaction',
            index=models.Index(fields=['status'], name='devices_dev_status_74d321_idx'),
        ),
        migrations.AddIndex(
            model_name='sensordata',
            index=models.Index(fields=['device', '-timestamp'], name='devices_sen_device__859ff1_idx'),
        ),
    ]