from django.db import models
from products.models import Product


class AttributeType(models.Model):
    name = models.CharField(max_length=20)
    # type = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Suffix(models.Model):
    name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    type = models.ForeignKey(AttributeType, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class AttributeSuffix(models.Model):
    attribute = models.OneToOneField(Attribute, on_delete=models.CASCADE, primary_key=True)
    suffix = models.ForeignKey(Suffix, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.attribute) + " has " + str(self.suffix)


class Option(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class OptionValue(models.Model):
    class Meta:
        unique_together = (('product', 'option'),)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return "[" + str(self.product) + "]'s [" + str(self.option.attribute.name) + "] = " + str(self.option.name)

    def get_val_tbl(self):
        return self.option


class IntValue(models.Model):
    class Meta:
        unique_together = (('product', 'attribute'),)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "[" + str(self.product) + "]'s [" + str(self.attribute) + "] = " + str(self.value)# + str(
           # self.attribute.attributesuffix.suffix)

    def get_val_tbl(self):
        return self


class FloatValue(models.Model):
    class Meta:
        unique_together = (('product', 'attribute'),)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.FloatField(default=0)

    def __str__(self):
        return "[" + str(self.product) + "]'s [" + str(self.attribute) + "] = " + str(self.value)# + str(
         #   self.attribute.attributesuffix.suffix) if AttributeSuffix.objects.filter(attribute=self.attribute).exists else ''

    def get_val_tbl(self):
        return self


class VarcharValue(models.Model):
    class Meta:
        unique_together = (('product', 'attribute'),)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, default=None)

    def __str__(self):
        return "[" + str(self.product) + "]'s [" + str(self.attribute) + "] = " + str(self.value)

    def get_val_tbl(self):
        return self
