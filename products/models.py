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


class Image(models.Model):
    url = models.ImageField(null=True, blank=True, default=None, upload_to='images', width_field="width",
                            height_field="height")
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    def __str__(self):
        return str(self.url)


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_DEFAULT, null=True, default=None)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_DEFAULT, null=True, default=None)
    title_image = models.ForeignKey(Image, null=True, default=None, on_delete=models.SET_DEFAULT)
    images = models.ManyToManyField(Image, related_name="products")
    price = models.FloatField(default=0)
    name = models.CharField(default=None, max_length=100)
    description = models.TextField(null=True, default=None)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name
