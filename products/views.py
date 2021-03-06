from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from attributes.models import *
import json
from django.core.serializers.json import DjangoJSONEncoder
from .methods import *
from django.views.generic import View
import re
from django.http import Http404
from orders.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import connection


def index(request):
    all_categories = Category.objects.all()
    data = []
    if request.user.is_authenticated:
        data.append(request.user.id)
        query = '''SELECT p.*, if(pl.id IS NOT NULL, 1, 0) AS liked, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p
        LEFT JOIN (SELECT id, product_id FROM customers_productlike WHERE customer_id = %s) AS pl
        ON p.id = pl.product_id
        LEFT JOIN (SELECT product_id, AVG(rate) AS rating FROM customers_productrate GROUP BY product_id) AS pr
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

    q2 = ''
    for p in request.COOKIES:
        if p != 'csrftoken' and p != 'sessionid':
            q2 += '(SELECT id, %s AS hits FROM attributes_option WHERE id = %s) UNION ' % (request.COOKIES[p], p)

    if q2[-7:] == ' UNION ':
        q2 = q2[:-7]

    if q2 == '':
        recommended = Product.objects.none()
    elif request.user.is_authenticated:
        recommended = Product.objects.raw('''
        SELECT p.id, p.price, p.name, p.description, p.subcategory_id, liked, if(AVG(pr.rate) IS NULL, 0, AVG(pr.rate))*p.hits AS relevance FROM
        (SELECT p.*, if(pl.id IS NOT NULL, 1, 0) AS liked, SUM(h.hits) AS hits FROM products_product p
        LEFT JOIN (SELECT id, product_id FROM customers_productlike WHERE customer_id = %s) AS pl
        ON p.id = pl.product_id
        JOIN attributes_optionvalue ov ON p.id = ov.product_id
        JOIN ({0}) AS h ON h.id = ov.option_id
        GROUP BY p.id, p.price, p.name, p.description, p.subcategory_id) AS p
        LEFT JOIN
        customers_productrate pr ON p.id=pr.product_id
        GROUP BY p.id, p.price, p.name, p.description, p.subcategory_id
        ORDER BY relevance DESC
    '''.format(q2), [request.user.id])
    else:
        recommended = Product.objects.raw('''
        SELECT p.id, p.price, p.name, p.description, p.subcategory_id, if(AVG(pr.rate) IS NULL, 0, AVG(pr.rate))*p.hits AS relevance FROM
        (SELECT p.*, SUM(h.hits) AS hits FROM products_product AS p
        JOIN attributes_optionvalue AS ov ON p.id = ov.product_id
        JOIN (%s) AS h ON h.id = ov.option_id
        GROUP BY p.id, p.price, p.name, p.description, p.subcategory_id) AS p
        LEFT JOIN
        customers_productrate AS pr ON p.id=pr.product_id
        GROUP BY p.id, p.price, p.name, p.description, p.subcategory_id
        ORDER BY relevance DESC
    ''' % q2)

    return render(request, 'index.html',
                  {'all_categories': all_categories, 'products': top_products, 'recommended': recommended})


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
        LEFT JOIN (SELECT product_id, AVG(rate) AS rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        WHERE (sc.id = %s)'''
    else:
        data.append(subcategory.id)
        query = '''SELECT p.id, p.name, p.price, if(pr.rating IS NULL, 0, pr.rating) AS rating
        FROM products_product p
        JOIN products_subcategory sc ON p.subcategory_id = sc.id
        LEFT JOIN (SELECT product_id, AVG(rate) AS rating FROM customers_productrate GROUP BY product_id) AS pr
        ON p.id=pr.product_id
        WHERE (sc.id = %s)'''

    if 'search' in request.GET and len(request.GET['search']):
        data.append('%' + request.GET['search'] + '%')
        query += " AND (p.name LIKE %s)"

    if 'option' in attrs:
        query = option_filter(query, attrs['option'], data)
    if 'int' in attrs:
        query = int_filter(query, attrs['int'], data)
    if 'float' in attrs:
        query = float_filter(query, attrs['float'], data)

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
    SELECT iv.id AS id, a.name AS name, CONCAT(iv.value, IF(s.name IS NOT NULL, s.name, '')) AS val
    FROM attributes_intvalue iv
    JOIN attributes_attribute a ON iv.attribute_id = a.id
    LEFT JOIN attributes_attributesuffix atsuf ON atsuf.attribute_id = a.id
    LEFT JOIN attributes_suffix s ON atsuf.suffix_id = s.id
    WHERE iv.product_id = %(id)s
    UNION
    SELECT fv.id AS id, a.name AS name, CONCAT(fv.value, IF(s.name IS NOT NULL, s.name, '')) AS val
    FROM attributes_floatvalue fv
    JOIN attributes_attribute a ON fv.attribute_id = a.id
    LEFT JOIN attributes_attributesuffix atsuf ON atsuf.attribute_id = a.id
    LEFT JOIN attributes_suffix s ON atsuf.suffix_id = s.id
    WHERE fv.product_id = %(id)s
    UNION
    SELECT vcv.id AS id, a.name AS name, vcv.value AS val
    FROM attributes_varcharvalue vcv
    JOIN attributes_attribute a ON vcv.attribute_id = a.id
    WHERE vcv.product_id = %(id)s
    ''', {'id': product_id})

    images = product.images.all()

    response = render(request, 'product_info.html',
                      {'all_categories': all_categories, 'product': product, 'attributes': attributes,
                       'images': images})

    opts = Option.objects.filter(optionvalue__product=product).values('id')
    list_opts = [x['id'] for x in opts]

    for o in list_opts:
        if str(o) in request.COOKIES.keys():
            response.set_cookie(str(o), str(int(request.COOKIES[str(o)]) + 1))
        else:
            response.set_cookie(str(o), 1)

    return response


class AddProductView(View):
    template_name = 'add_product.html'

    def get(self, request):
        if not request.user.is_superuser:
            raise Http404()
        all_categories = Category.objects.all()
        return render(request, self.template_name, {'all_categories': all_categories})

    def post(self, request):
        if not request.user.is_superuser:
            raise Http404()
        subcategory = get_object_or_404(Subcategory, name=request.POST.get('subcategory').lower())
        product = Product.objects.create(
            name=request.POST.get('name'), price=request.POST.get('price'), description=request.POST.get('description'),
            title_image=request.POST.get('image')
        )
        product.subcategory = subcategory
        product.save()
        attributes = request.POST.get('attributes')
        for attribute in attributes.split('\n'):
            parts = list(map(lambda x: x.strip().lower(), attribute.split('-')))
            if re.match('int', parts[1], re.IGNORECASE) and re.match('^[0-9]+$', parts[2]):
                xtype = AttributeType.objects.get(name='int')
                attr = Attribute.objects.get_or_create(type=xtype, name=parts[0])[0]
                IntValue.objects.create(product=product, attribute=attr, value=parts[2])
            elif re.match('fl|fr', parts[1], re.IGNORECASE) and re.match('^[0-9]+(?:\.[0-9]+)?$', parts[2]):
                xtype = AttributeType.objects.get(name='float')
                attr = Attribute.objects.get_or_create(type=xtype, name=parts[0])[0]
                FloatValue.objects.create(product=product, attribute=attr, value=parts[2])
            elif re.match('op', parts[1], re.IGNORECASE):
                xtype = AttributeType.objects.get(name='option')
                attr = Attribute.objects.get_or_create(type=xtype, name=parts[0])[0]
                opt = Option.objects.get_or_create(attribute=attr, name=parts[2])[0]
                OptionValue.objects.create(product=product, option=opt)
            elif re.match('str|ch', parts[1], re.IGNORECASE):
                xtype = AttributeType.objects.get(name='varchar')
                attr = Attribute.objects.get_or_create(type=xtype, name=parts[0])[0]
                VarcharValue.objects.create(product=product, attribute=attr, value=parts[2])
            else:
                raise Http404('incorrect attribute type')
            all_categories = Category.objects.all()
        return render(request, self.template_name, {'all_categories': all_categories})


def statistics(request):
    if not request.user.is_superuser:
        raise Http404()

    cursor = connection.cursor()
    cursor.execute('''
        SELECT MONTH(o.timestamp) AS month, YEAR(o.timestamp) AS year, SUM(pr.price * pur.amount) AS sum FROM products_product AS pr
        JOIN orders_purchase AS pur ON pr.id = pur.product_id
        JOIN orders_basket AS b ON pur.basket_id = b.id
        JOIN orders_order AS o ON b.order_id = o.id
        GROUP BY month
        ORDER BY sum DESC
        ''')

    months_stat2json = [{'month': x[0], 'year': x[1], 'sum': x[2]} for x in cursor.fetchall()]

    all_categories = Category.objects.all()
    return render(request, 'statistics.html',
                  {'months_stat': json.dumps(months_stat2json, cls=DjangoJSONEncoder),
                   'all_categories': all_categories})


def subcategory_manufacturer_stat(request, subcategory_name):
    if not request.user.is_superuser:
        raise Http404()

    manufacturers = Option.objects.raw('''
        SELECT opt.id, opt.name AS manufacturer, SUM(pr.price*pur.amount) AS sum FROM products_product AS pr
        JOIN orders_purchase AS pur ON pr.id = pur.product_id
        JOIN orders_basket AS b ON pur.basket_id = b.id
        JOIN orders_order AS ord ON b.order_id = ord.id
        JOIN products_subcategory AS sc ON pr.subcategory_id = sc.id
        JOIN attributes_optionvalue AS ov ON pr.id = ov.product_id
        JOIN attributes_option AS opt ON ov.option_id = opt.id
        JOIN attributes_attribute AS a ON opt.attribute_id = a.id
        WHERE b.order_id IS NOT NULL
        AND a.name = 'manufacturer'
        AND sc.name = '%s'
        AND ord.timestamp BETWEEN (CURDATE() - INTERVAL 30 DAY) AND (CURDATE() + INTERVAL 1 DAY)
        GROUP BY opt.id, opt.name
    ''' % subcategory_name)

    manufacturers2json = [{'manufacturer': x.manufacturer, 'sum': x.sum} for x in manufacturers]

    return HttpResponse(json.dumps(manufacturers2json))


def categories_cost_report(request):
    if not request.user.is_superuser:
        raise Http404()

    subcategories = Category.objects.raw('''
    SELECT sc.id, sc.name, SUM(pr.price * pur.amount) AS sum
    FROM products_subcategory AS sc
    JOIN products_product AS pr ON sc.id = pr.subcategory_id
    JOIN orders_purchase AS pur ON pr.id = pur.product_id
    JOIN orders_basket AS b ON pur.basket_id = b.id
    JOIN orders_order AS o ON b.order_id = o.id
    WHERE o.timestamp BETWEEN (CURDATE() - INTERVAL 30 DAY) AND (CURDATE() + INTERVAL 1 DAY)
    GROUP BY sc.id, sc.name
    ORDER BY sum DESC
    ''')

    sum = 0
    for x in subcategories:
        sum += x.sum

    return render(request, 'categories_cost_report.html', {'subcategories': subcategories, 'sum': sum})


def categories_amount_report(request):
    if not request.user.is_superuser:
        raise Http404()

    subcategories = Category.objects.raw('''
        SELECT sc.id, sc.name, COUNT(*) AS count
        FROM products_subcategory AS sc
        JOIN products_product AS pr ON sc.id = pr.subcategory_id
        JOIN orders_purchase AS pur ON pr.id = pur.product_id
        JOIN orders_basket AS b ON pur.basket_id = b.id
        JOIN orders_order AS o ON b.order_id = o.id
        WHERE o.timestamp BETWEEN (CURDATE() - INTERVAL 30 DAY) AND (CURDATE() + INTERVAL 1 DAY)
        GROUP BY sc.id, sc.name
        ORDER BY count DESC
        ''')

    sum = 0
    for x in subcategories:
        sum += x.count

    return render(request, 'categories_amount_report.html', {'subcategories': subcategories, 'sum': sum})
