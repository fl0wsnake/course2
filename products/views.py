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

    query = '''SELECT p.id, p.name, p.price, p.rating
    FROM products_product p
    JOIN products_subcategory sc ON p.subcategory_id = sc.id
    LEFT JOIN attributes_optionvalue ov ON p.id = ov.product_id
    LEFT JOIN attributes_intvalue iv ON p.id = iv.product_id
    LEFT JOIN attributes_floatvalue fv ON p.id = fv.product_id
    LEFT JOIN attributes_varcharvalue vcv ON p.id = vcv.product_id
    WHERE (sc.id = %(cat)s) AND'''

    raw_data = {'cat': subcategory_id}
    d = {}
    for attr in request.GET:
        if attr not in d:
            d[attr] = [request.GET[attr]]
        else:
            d[attr].append[request.GET[attr]]

    for attr in request.GET:
        attr_type = Attribute.objects.get(id=attr).type
        if attr_type.type == "num":
            gap = request.GET[attr].split('-')
            raw_data[attr + '0'] = gap[0]
            raw_data[attr + '1'] = gap[1]
            query += ' (attributes_' + attr_type + '.value BETWEEN %(' + attr + '0)s AND %(' + attr + '1)s) AND'
        else:
            raw_data[attr + '2'] = request.GET[attr]
            query += ' (ov.option_id = %(' + attr + '2)s) AND'

    if query[-4:] == ' AND':
        query = query[:-4]

    products = Product.objects.raw(query, raw_data)

    return render(request, 'index/index.html', {'all_categories': all_categories,
                                                'subcategory': subcategory,
                                                'products': products})


# SELECT product.name FROM products JOIN _value JOIN attribute WHERE attribute = {attr} AND _value={val}

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
