# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_auto_incrementing_pk_field(apps, schema_editor):
    MultiToken = apps.get_model('django_rest_multitokenauth', 'MultiToken')

    # Generate values for the new id column
    for i, o in enumerate(MultiToken.objects.all()):
        o.id = i + 1
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('django_rest_multitokenauth', '0002_rename_ip_address_20160426',),
    ]

    operations = [
        migrations.AddField(
            model_name='multitoken',
            name='id',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.RunPython(
            populate_auto_incrementing_pk_field,
            migrations.RunPython.noop
        ),
        # add primary key information to id field
        migrations.AlterField(
            model_name='multitoken',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False)
        ),
        # remove primary key information from 'key' field
        migrations.AlterField(
            model_name='multitoken',
            name='key',
            field=models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Key'),
        ),
    ]
