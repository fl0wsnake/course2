from django.contrib import admin
from products.models import *

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Image)
admin.site.register(Product)