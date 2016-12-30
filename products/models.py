from django.db import models
from django.db.models import Avg
from django.db.models import Sum
from django.db import connection


class Category(models.Model):
    name = models.CharField(max_length=100)

    def get_subcategories(self):
        return Subcategory.objects.filter(category=self)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, null=True, default=None)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    # def get_sum(self):
    #     with connection.cursor() as cursor:
    #         cursor.execute('''
    #             SELECT IF(sum IS NOT NULL, sum, 0) FROM (SELECT SUM(pr.price * pur.amount) AS sum FROM products_subcategory AS sc
    #              JOIN products_product AS pr ON sc.id = pr.subcategory_id
    #              JOIN orders_purchase AS pur ON pr.id = pur.product_id
    #              JOIN orders_basket AS b ON pur.basket_id = b.id
    #              WHERE b.order_id IS NOT NULL
    #              AND sc.id = %s) AS t
    #         ''' % self.id)
    #         return cursor.fetchone()[0]


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

            # def liked(self, customer):
            #     return self.productlike_set.filter(customer=customer).exists()
            # return ProductLike.filter(product=self, customer=customer)
