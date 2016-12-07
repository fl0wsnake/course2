from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *
import json
from django.core.serializers.json import DjangoJSONEncoder
from .methods import *


def index(request):
    all_categories = Category.objects.all()
    data = []
    if request.user.is_authenticated:
        data.append(request.user.id)
        query = '''SELECT p.*, if(pl.id IS NOT NULL, 1, 0) AS liked, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p
        LEFT JOIN (SELECT id, product_id FROM customers_productlike WHERE customer_id = %s) AS pl
        ON p.id = pl.product_id
        LEFT JOIN (SELECT product_id, AVG(rate) as rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        '''
    else:
        query = '''SELECT p.*, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p
        LEFT JOIN (SELECT product_id, AVG(rate) AS rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        '''
    top_products = Product.objects.raw(
        sort_query(query, request) + ' LIMIT 16', data)
    return render(request, 'index.html', {'all_categories': all_categories, 'products': top_products})


def subcategory_products(request, subcategory_name):
    subcategory = get_object_or_404(Subcategory, name=subcategory_name)
    all_categories = Category.objects.all()

    attrs = parseUrl(request)
    data = []

    if request.user.is_authenticated:
        data.append(request.user.id)
        data.append(subcategory.id)
        query = '''SELECT p.*, if(pl.id IS NOT NULL, 1, 0) AS liked, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p LEFT JOIN
        (SELECT id, product_id FROM customers_productlike WHERE customer_id = %s) AS pl ON p.id = pl.product_id
        JOIN products_subcategory sc ON p.subcategory_id = sc.id
        LEFT JOIN (SELECT product_id, AVG(rate) as rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        WHERE (sc.id = %s)'''
    else:
        data.append(subcategory.id)
        query = '''SELECT p.id, p.name, p.price, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p
        JOIN products_subcategory sc ON p.subcategory_id = sc.id
        LEFT JOIN (SELECT product_id, AVG(rate) as rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        WHERE (sc.id = %s)'''

    if 'search' in request.GET and len(request.GET['search']):
        data.append('%' + request.GET['search'] + '%')
        query += " AND (p.name LIKE %s)"

    if 'optionvalue' in attrs:
        query = option_filter(query, attrs['optionvalue'], data)
    if 'intvalue' in attrs:
        query = int_filter(query, attrs['intvalue'], data)
    if 'floatvalue' in attrs:
        query = float_filter(query, attrs['floatvalue'], data)

    query = sort_query(query, request)

    products = Product.objects.raw(query, data)

    filters_query = Attribute.objects.raw('''
    SELECT DISTINCT a.id, a.name AS attr, o.name AS opt, COUNT(ov.product_id) AS prod_num
    FROM products_product p
    JOIN attributes_optionvalue ov ON p.id = ov.product_id
    JOIN attributes_option o ON ov.option_id = o.id
    JOIN attributes_attribute a ON o.attribute_id = a.id
    WHERE p.subcategory_id = %s
    GROUP BY a.id, attr, opt
    HAVING prod_num > 0
    ORDER BY a.id
    ''', [subcategory.id])

    filters = make_2d_filters(filters_query)

    return render(request, 'subcategory_products.html', {'all_categories': all_categories,
                                                         'title': subcategory.name,
                                                         'products': products,
                                                         'filters': json.dumps(filters,
                                                                               cls=DjangoJSONEncoder)
                                                         })


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

    return render(request, 'product_info.html',
                  {'all_categories': all_categories, 'product': product, 'attributes': attributes, 'images': images})
