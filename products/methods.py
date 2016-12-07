from django.shortcuts import get_object_or_404
from attributes.models import Attribute


def sort_query(query, request):
    if 'sort' in request.GET:
        str = request.GET['sort']
    else:
        str = 'rating'
    return query + (
        ' ORDER BY p.price' if str == 'price' else ' ORDER BY p.price DESC' if str == 'priceDesc' else ' ORDER BY pr.rating DESC')


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
