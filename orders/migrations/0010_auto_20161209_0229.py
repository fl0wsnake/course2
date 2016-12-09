# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-09 00:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20161209_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='order',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='basket', to='orders.Order'),
        ),
    ]
