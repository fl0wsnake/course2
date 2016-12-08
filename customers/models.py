from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class ProductLike(models.Model):
    class Meta:
        unique_together = (('customer', 'product'),)

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class ProductRate(models.Model):
    class Meta:
        unique_together = (('customer', 'product'),)

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.FloatField()

    def __str__(self):
        return str(self.customer.first_name) + ' ' + self.product.name + ' ' + str(self.rate)
