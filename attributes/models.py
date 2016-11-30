from django.db import models
from products.models import Product


class AttributeType(models.Model):
    name = models.CharField(max_length=50)


class Attribute(models.Model):
    type = models.ForeignKey(AttributeType, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)


class Suffix(models.Model):
    name = models.CharField(max_length=50)


class Option(models.Model):
    name = models.CharField(max_length=50)


class OptionValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    option = models.ForeignKey(Option, on_delete=models.PROTECT)


class IntValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    value = models.IntegerField(default=0)


class FloatValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    value = models.FloatField(default=0)


class VarcharValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    value = models.CharField(max_length=100, default=None)
