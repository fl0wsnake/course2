from django.db import models
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=100)

    def get_subcategories(self):
        return self.subcategory_set.all()

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, null=True, default=None)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Image(models.Model):
    img = models.ImageField(upload_to='images/', width_field="width",
                            height_field="height")
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    def __str__(self):
        return str(self.img.url)


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_DEFAULT, null=True, default=None)
    title_image = models.ForeignKey(Image, null=True, default=None, on_delete=models.SET_DEFAULT)
    images = models.ManyToManyField(Image, related_name="products", blank=True)
    price = models.FloatField(default=0)
    name = models.CharField(default=None, max_length=100)
    description = models.TextField(null=True, default=None)

    def __str__(self):
        return self.name.title()

    def rating(self):
        if self.productrate_set.exists():
            return self.productrate_set.aggregate(Avg('rate'))['rate__avg']
        else:
            return 0
