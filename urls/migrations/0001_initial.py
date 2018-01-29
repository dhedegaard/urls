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
            name='Url',
            fields=[
                ('keyword', models.TextField(max_length=100, serialize=False,
                                             primary_key=True)),
                ('url', models.TextField(max_length=2048)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('proxy', models.BooleanField(default=False)),
                ('public', models.BooleanField(default=False)),
                ('user', models.ForeignKey(
                    to=settings.AUTH_USER_MODEL,
                    db_column='user', on_delete=models.SET_NULL, null=True)),
            ],
            options={
                'ordering': ['keyword'],
            },
            bases=(models.Model,),
        ),
    ]
