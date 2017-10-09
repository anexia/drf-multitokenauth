# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiToken',
            fields=[
                ('key', models.CharField(serialize=False, max_length=64, primary_key=True, verbose_name='Key')),
                ('created', models.DateTimeField(verbose_name='Created', auto_now_add=True)),
                ('last_known_IP', models.GenericIPAddressField(default='127.0.0.1', verbose_name='The IP address of this session')),
                ('user_agent', models.CharField(default='', max_length=256, verbose_name='HTTP User Agent')),
                ('user', models.ForeignKey(related_name='auth_tokens', verbose_name='User', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Tokens',
                'verbose_name': 'Token',
                'abstract': False,
            },
        ),
    ]
