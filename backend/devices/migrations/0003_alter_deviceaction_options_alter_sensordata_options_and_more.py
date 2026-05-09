from django.db import migrations, models
from django.db.models import deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_device_platform_expansion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deviceaction',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='sensordata',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='home',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='home',
            name='owner',
            field=models.ForeignKey(on_delete=deletion.CASCADE, related_name='owned_homes', to='auth.user'),
        ),
        migrations.AlterField(
            model_name='home',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.CharField(choices=[('thermometer', 'Termometr'), ('lock', 'Zamek elektroniczny'), ('light', 'Oświetlenie'), ('smoke_detector', 'Czujnik dymu'), ('generic_sensor', 'Czujnik ogólny'), ('actuator', 'Aktuator')], max_length=20),
        ),
        migrations.AlterField(
            model_name='device',
            name='home',
            field=models.ForeignKey(on_delete=deletion.CASCADE, related_name='devices', to='devices.home'),
        ),
        migrations.AlterField(
            model_name='device',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='deviceaction',
            name='device',
            field=models.ForeignKey(on_delete=deletion.CASCADE, related_name='actions', to='devices.device'),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='device',
            field=models.ForeignKey(on_delete=deletion.CASCADE, related_name='readings', to='devices.device'),
        ),
    ]