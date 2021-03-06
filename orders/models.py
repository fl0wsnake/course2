from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from django.db.models import Sum


class OrderStatus(models.Model):
    status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.status)


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default=2)
    customer_name = models.CharField(max_length=50, null=True, default=None)
    address = models.CharField(max_length=50, null=True, default=None)
    phone_number = models.CharField(max_length=50, null=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_purchases(self):
        return Product.objects.filter(purchase__basket__order=self)

    def get_sum(self):
        return self.get_purchases().aggregate(Sum('price'))['price__sum']


class Basket(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, default=None, related_name='basket')

    def __str__(self):
        return str(self.customer.username) + "'s"


class Purchase(models.Model):
    class Meta:
        unique_together = ('product', 'basket')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basket = models.ForeignKey(Basket, related_name='purchases', on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    def __str__(self):
        return self.basket.customer.username + "'s " + str(self.product)
