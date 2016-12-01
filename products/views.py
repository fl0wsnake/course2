from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *


# from django.views.decorators.http import require_http_methods


def index(request):
    all_categories = Category.objects.all()
    top_products = Product.objects.raw('SELECT * FROM products_product ORDER BY products_product.rating LIMIT 16')
    return render(request, 'index/index.html', {'all_categories': all_categories, 'products': top_products})


def subcategory_products(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    all_categories = Category.objects.all()

    

    return render(request, 'index/index.html', {'all_categories': all_categories,
                                                'subcategory': subcategory,
                                                'products': subcategory.product_set.all()})


def product_info(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    all_categories = Category.objects.all()

    attributes = Attribute.objects.raw('''
    SELECT ov.id AS id, a.name AS name, o.name AS val
    FROM attributes_optionvalue ov
    JOIN attributes_option o ON ov.option_id = o.id
    JOIN attributes_attribute a ON o.attribute_id = a.id
    WHERE ov.product_id = %(id)s
    UNION
    SELECT iv.id AS id, a.name AS name, CONCAT(iv.value, s.name) AS val
    FROM attributes_intvalue iv
    JOIN attributes_attribute a ON iv.attribute_id = a.id
    JOIN attributes_attributesuffix atsuf ON atsuf.attribute_id = a.id
    JOIN attributes_suffix s ON atsuf.suffix_id = s.id
    WHERE iv.product_id = %(id)s
    UNION
    SELECT fv.id AS id, a.name AS name, CONCAT(fv.value, s.name) AS val
    FROM attributes_floatvalue fv
    JOIN attributes_attribute a ON fv.attribute_id = a.id
    JOIN attributes_attributesuffix atsuf ON atsuf.attribute_id = a.id
    JOIN attributes_suffix s ON atsuf.suffix_id = s.id
    WHERE fv.product_id = %(id)s
    UNION
    SELECT vcv.id AS id, a.name AS name, vcv.value AS val
    FROM attributes_varcharvalue vcv
    JOIN attributes_attribute a ON vcv.attribute_id = a.id
    WHERE vcv.product_id = %(id)s
    ''', {'id': product_id})

    images = product.images.all()

    return render(request, 'product_info/product_info.html',
                  {'all_categories': all_categories, 'product': product, 'attributes': attributes, 'images': images})


# @require_http_methods(['POST'])
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return redirect('/product/' + product_id)
