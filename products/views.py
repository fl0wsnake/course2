from django.shortcuts import render, get_object_or_404
from .models import *


def index(request):
    all_categories = Category.objects.select_related().all()
    top_products = Product.objects.raw('SELECT * FROM `products_product` ORDER BY `products_product`.`rating` LIMIT 16')
    return render(request, 'index/index.html', {'all_categories': all_categories, 'top_products': top_products})


def products_of_subcategory(request, subcategory_id):
    category = get_object_or_404(Subcategory, id=subcategory_id)


def product_info(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_info/product_info.html', {'product': product})
