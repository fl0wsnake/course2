from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *
from django.db import connection
import json
from django.core.serializers.json import DjangoJSONEncoder


# from django.views.decorators.http import require_http_methods

def get_filtered_products(query, filters, raw_data):
    options = {}
    for attr in filters:
        attr_type = get_object_or_404(Attribute, name=attr).type
        if attr_type.type == "num":
            gap = filters[attr].split('-')
            raw_data.append(gap[0])
            raw_data.append(gap[1])
            query += ' (' + ('iv' if attr_type.name == 'intvalue' else 'fv') + '.value BETWEEN %s AND %s) AND'
        elif attr_type.type == "option":
            options[attr] = filters.getlist(attr)

    query += ' ('
    for attr in options:
        for opt in options[attr]:
            raw_data.append(opt)
            query += '(LOWER(o.name) = %s) OR '

    if query[-6:] == ' AND (':
        query = query[:-6]
    else:
        query = query[:-4] + ')'

    query += ' GROUP BY p.id, p.name, p.price, p.rating HAVING count >= %s' % len(options)

    return query


def index(request):
    all_categories = Category.objects.all()
    top_products = Product.objects.raw('SELECT * FROM products_product ORDER BY products_product.rating LIMIT 16')
    return render(request, 'index/index.html', {'all_categories': all_categories, 'products': top_products})


def subcategory_products(request, subcategory_name):
    subcategory = get_object_or_404(Subcategory, name=subcategory_name)
    all_categories = Category.objects.all()
    cursor = connection.cursor

    query = '''SELECT p.id, p.name, p.price, p.rating, COUNT(*) AS count
    FROM products_product p
    JOIN products_subcategory sc ON p.subcategory_id = sc.id
    LEFT JOIN attributes_optionvalue ov ON p.id = ov.product_id
    LEFT JOIN attributes_option o ON ov.option_id = o.id
    LEFT JOIN attributes_intvalue iv ON p.id = iv.product_id
    LEFT JOIN attributes_floatvalue fv ON p.id = fv.product_id
    LEFT JOIN attributes_varcharvalue vcv ON p.id = vcv.product_id
    WHERE (sc.id = %s) AND'''

    raw_data = [subcategory.id]
    products = Product.objects.raw(get_filtered_products(query, request.GET, raw_data), raw_data)

    filters_query = Attribute.objects.raw('''
    SELECT DISTINCT a.id, a.name AS attr, o.name AS opt, COUNT(ov.product_id) AS prod_num
    FROM products_product p
    JOIN attributes_optionvalue ov ON p.id = ov.product_id
    JOIN attributes_option o ON ov.option_id = o.id
    JOIN attributes_attribute a ON o.attribute_id = a.id
    WHERE p.subcategory_id = %(cat)s
    GROUP BY a.id, attr, opt
    HAVING prod_num > 0
    ORDER BY a.id
    ''', {'cat': subcategory.id})

    # from collections import defaultdict
    # groups = defaultdict(dict)
    # for obj in filters_query:
    #     groups[obj.attr].append(obj)
    #
    # filters = groups.values()
    filters = []
    # for opt in filters_query:
    #     if opt.attr not in filters:
    #         filters[opt.attr] = [{'opt': opt.opt, 'prod_num': opt.prod_num}]
    #     else:
    #         filters[opt.attr].append({'opt': opt.opt, 'prod_num': opt.prod_num})
    prev_attr = '0'
    i = -1
    for opt in filters_query:
        if opt != prev_attr:
            filters.append({'attr': opt.attr, 'opts': [{'opt': opt.opt, 'prod_num': opt.prod_num}]})
            prev_attr = opt.attr
            i += 1
        else:
            filters[i].opts.append({'opt': opt.opt, 'prod_num': opt.prod_num})

    return render(request, 'subcategory_products/subcategory_products.html', {'all_categories': all_categories,
                                                                              'subcategory': subcategory,
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

    return render(request, 'product_info/product_info.html',
                  {'all_categories': all_categories, 'product': product, 'attributes': attributes, 'images': images})


# @require_http_methods(['POST'])
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return redirect('/product/' + product_id)
