from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *
import json
from django.core.serializers.json import DjangoJSONEncoder


# from django.views.decorators.http import require_http_methods


def sort_query(query, request):
    if 'sort' in request.GET:
        str = request.GET['sort']
    else:
        str = 'rating'
    return query + (
        ' ORDER BY p.price' if str == 'price' else ' ORDER BY p.price DESC' if str == 'priceDesc' else ' ORDER BY p.rating DESC')


def get_filtered_products(query, filters, raw_data):
    options = {}
    for attr in filters:
        attr_type = get_object_or_404(Attribute, name=attr).type
        if attr_type.type == "num":

            gap = filters[attr].split('-')
            raw_data.append(attr)
            raw_data.append(gap[0])
            raw_data.append(gap[1])
            query += ' (LOWER(a.name) = %s AND ' + (
                '(iv' if attr_type.name == 'intvalue' else 'fv') + '.value BETWEEN %s AND %s)) AND'
        elif attr_type.type == "option":
            options[attr] = filters.getlist(attr)

    query += ' ('
    for attr in options:
        for opt in options[attr]:
            raw_data.append(attr)
            raw_data.append(opt)
            query += '(LOWER(a.name) = %s AND LOWER(o.name) = %s) OR '

    if query[-6:] == ' AND (':
        query = query[:-6]
    else:
        query = query[:-4] + ')'

    query += ' GROUP BY p.id, p.name, p.price, p.rating HAVING count >= %s' % len(options)

    return query


def index(request):
    all_categories = Category.objects.all()
    top_products = Product.objects.raw(
        sort_query('SELECT * FROM products_product p', request) + ' LIMIT 16')
    return render(request, 'index.html', {'all_categories': all_categories, 'products': top_products})


def option_filter(query, attrs, data):
    query = '''SELECT p.id, p.name, p.price, p.rating, COUNT(*) AS count
    FROM (%s) as p
    LEFT JOIN attributes_optionvalue ov ON p.id = ov.product_id
    LEFT JOIN attributes_option o ON ov.option_id = o.id
    LEFT JOIN attributes_attribute a ON o.attribute_id = a.id
    WHERE
    ''' % query
    for attr in attrs:
        for opt in attrs[attr]:
            data.append(attr)
            data.append(opt)
            query += '(LOWER(a.name) = %s AND LOWER(o.name) = %s) OR '

    query = query[:-4]
    query += ' GROUP BY p.id, p.name, p.price, p.rating HAVING count = %s' % len(attrs)

    return query


def int_filter(query, attrs, data):
    query = '''SELECT p.id, p.name, p.price, p.rating, COUNT(*) AS count
    FROM (%s) as p
    LEFT JOIN attributes_intvalue iv ON p.id = iv.product_id
    LEFT JOIN attributes_attribute a ON iv.attribute_id = a.id
    WHERE
    ''' % query
    for attr in attrs:
        gap = attrs[attr][0].split('-')
        data.append(attr)
        data.append(gap[0])
        data.append(gap[1])
        query += ' (LOWER(a.name) = %s AND (iv.value BETWEEN %s AND %s)) AND'

    query = query[:-4]
    query += ' GROUP BY p.id, p.name, p.price, p.rating HAVING count = %s' % len(attrs)

    return query


def float_filter(query, attrs, data):
    query = '''SELECT p.id, p.name, p.price, p.rating, COUNT(*) AS count
    FROM (%s) as p
    LEFT JOIN attributes_floatvalue fv ON p.id = fv.product_id
    LEFT JOIN attributes_attribute a ON fv.attribute_id = a.id
    WHERE
    ''' % query
    for attr in attrs:
        gap = attrs[attr][0].split('-')
        data.append(attr)
        data.append(gap[0])
        data.append(gap[1])
        query += ' (LOWER(a.name) = %s AND (fv.value BETWEEN %s AND %s)) AND'

    query = query[:-4]
    query += ' GROUP BY p.id, p.name, p.price, p.rating HAVING count = %s' % len(attrs)

    return query


def parseUrl(request):
    attrs = {}
    for attr in request.GET:
        if (attr == 'sort') or (attr == 'search'):
            continue
        attr_type = get_object_or_404(Attribute, name=attr).type.name
        if attr_type not in attrs:
            attrs[attr_type] = {}
        if attr not in attrs[attr_type]:
            attrs[attr_type][attr] = []
        for opt in request.GET.getlist(attr):
            attrs[attr_type][attr].append(opt)
    return attrs


def make_2d_filters(filters_query):
    filters = []
    prev_attr = '0'
    for opt in filters_query:
        if opt.attr != prev_attr:
            filters.append({'attr': opt.attr, 'opts': [{'opt': opt.opt, 'prod_num': opt.prod_num}]})
            prev_attr = opt.attr
        else:
            filters[-1]['opts'].append({'opt': opt.opt, 'prod_num': opt.prod_num})
    return filters


def subcategory_products(request, subcategory_name):
    subcategory = get_object_or_404(Subcategory, name=subcategory_name)
    all_categories = Category.objects.all()

    attrs = parseUrl(request)
    data = [subcategory.id]

    query = '''SELECT p.id, p.name, p.price, p.rating
    FROM products_product p
    JOIN products_subcategory sc ON p.subcategory_id = sc.id
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


# @require_http_methods(['POST'])
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return redirect('/product/' + product_id)
