from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drf_multitokenauth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='multitoken',
            old_name='last_known_IP',
            new_name='last_known_ip',
        ),
    ]
