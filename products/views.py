from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *
from itertools import groupby


# from django.views.decorators.http import require_http_methods

def get_filtered_products(query, filters, raw_data):
    # WHERE str
    count = 0
    for attr in filters:
        attr_type = Attribute.objects.get(id=attr).type
        if attr_type.type == "num":
            gap = attr[0].split('-')
            raw_data[str(count)] = gap[0]
            count += 1
            raw_data[str(count)] = gap[1]
            count += 1
            query += ' (attributes_' + attr_type + '.value BETWEEN %(' + str(count - 2)
            ')s AND %(' + str(count - 1)
            ')s) AND'
        else:
            query += ' ('
            for val in filters.getlist(attr):
                raw_data[str(count)] = val
                query += '(ov.option_id = %(' + str(count) + ')s) OR '
                count += 1
            query = query[:-4] + ')'

    if query[-4:] == ' AND':
        query = query[:-4]

    return Product.objects.raw(query, raw_data)


def index(request):
    all_categories = Category.objects.all()
    top_products = Product.objects.raw('SELECT * FROM products_product ORDER BY products_product.rating LIMIT 16')
    return render(request, 'index/index.html', {'all_categories': all_categories, 'products': top_products})


def subcategory_products(request, subcategory_id):
    from django.db.models import Count

    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    all_categories = Category.objects.all()

    query = '''SELECT DISTINCT p.id, p.name, p.price, p.rating
    FROM products_product p
    JOIN products_subcategory sc ON p.subcategory_id = sc.id
    LEFT JOIN attributes_optionvalue ov ON p.id = ov.product_id
    LEFT JOIN attributes_intvalue iv ON p.id = iv.product_id
    LEFT JOIN attributes_floatvalue fv ON p.id = fv.product_id
    LEFT JOIN attributes_varcharvalue vcv ON p.id = vcv.product_id
    WHERE (sc.id = %(cat)s) AND'''

    products = get_filtered_products(query, request.GET, {'cat': subcategory_id})

    filters_query = Attribute.objects.raw('''
    SELECT DISTINCT a.id, a.name AS attr, o.name AS opt, COUNT(ov.product_id) AS prod_num
    FROM products_product p
    JOIN attributes_optionvalue ov ON p.id = ov.product_id
    JOIN attributes_option o ON ov.option_id = o.id
    JOIN attributes_attribute a ON o.attribute_id = a.id
    WHERE p.subcategory_id = %(cat)s
    GROUP BY a.id, attr, opt
    HAVING prod_num > 0
    ''', {'cat': subcategory_id})

    from collections import defaultdict
    groups = defaultdict(list)
    for obj in filters_query:
        groups[obj.id].append(obj)

    filters = groups.values()

    return render(request, 'subcategory_products/subcategory_products.html', {'all_categories': all_categories,
                                                                              'subcategory': subcategory,
                                                                              'products': products,
                                                                              'filters': filters
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
