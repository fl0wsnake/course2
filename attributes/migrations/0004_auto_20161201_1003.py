# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-01 08:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attributes', '0003_auto_20161201_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floatvalue',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='intvalue',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='optionvalue',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='varcharvalue',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
