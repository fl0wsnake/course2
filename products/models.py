from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def get_subcategories(self):
        return self.subcategory_set.all()

    def __str__(self):
        return self.name.title()


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, null=True, default=None)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name.title()


class Manufacturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_DEFAULT, null=True, default=None)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_DEFAULT, null=True, default=None)
    name = models.CharField(max_length=100)
    # image

    def __str__(self):
        return self.name
