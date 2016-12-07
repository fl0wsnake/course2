from django.db import models
from products.models import Product
from django.contrib.auth.models import User


class OrderStatus(models.Model):
    status = models.CharField(max_length=50)


class Basket(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')


class Purchase(models.Model):
    class Meta:
        unique_together = ('product', 'basket')

    product = models.ForeignKey(Product)
    basket = models.ForeignKey(Basket, related_name='purchases')
    amount = models.IntegerField(default=1)


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    basket = models.OneToOneField(Basket, on_delete=models.CASCADE)
    customername = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
