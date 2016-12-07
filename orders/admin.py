from django.contrib import admin
from .models import *

admin.site.register(OrderStatus)
admin.site.register(Basket)
admin.site.register(Purchase)
admin.site.register(Order)
