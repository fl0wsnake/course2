# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-07 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_product_rating'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='basket',
            name='products',
        ),
        migrations.AddField(
            model_name='purchase',
            name='basket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Basket'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
    ]
