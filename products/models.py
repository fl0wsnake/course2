from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Subcategory(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class Manufacturer(models.Model):
    name = models.CharField(max_length=100)


class Product(models.Model):
    subcategory_id = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    manufacturer_id = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    # image
