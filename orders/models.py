from django.db import models
from products.models import Product
from django.contrib.auth.models import User


class OrderStatus(models.Model):
    status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.status)


class Basket(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')

    def __str__(self):
        return str(self.customer.username) + "'s"


class Purchase(models.Model):
    class Meta:
        unique_together = ('product', 'basket')

    product = models.ForeignKey(Product)
    basket = models.ForeignKey(Basket, related_name='purchases')
    amount = models.IntegerField(default=1)

    def __str__(self):
        return self.basket.customer.username + "'s " + str(self.product)


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default=2)
    basket = models.OneToOneField(Basket, on_delete=models.CASCADE, null=True, default=None)
    customername = models.CharField(max_length=50, null=True, default=None)
    address = models.CharField(max_length=50, null=True, default=None)
    phone_number = models.CharField(max_length=50, null=True, default=None)

    def get_purchases(self):
        return self.basket.purchases
