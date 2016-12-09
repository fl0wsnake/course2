from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .forms import *
from django.contrib.auth import login
from .models import *
from django.http import HttpResponse
from orders.models import *
from products.models import Product, Category
from django.db.models import Sum
from django.db import connection


class RegisterFormView(View):
    form_class = RegisterForm
    template_name = 'register.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            # user.set_unusable_password()
            user.save()
            login(request, user)
            return redirect('index')

        return render(request, self.template_name, {'form': form})


def like_product(request, product_id):
    if not request.user.is_authenticated:
        return HttpResponse(0)
    if ProductLike.objects.filter(customer=request.user, product_id=product_id).exists():
        ProductLike.objects.get(customer=request.user, product_id=product_id).delete()
        return HttpResponse(0)
    ProductLike.objects.create(customer=request.user, product_id=product_id)
    return HttpResponse(1)


def rate_product(request, product_id, rate):
    if not request.user.is_authenticated:
        return HttpResponse(0)
    rate_float = float(rate)
    if rate_float < 0 or rate_float > 5 or rate_float * 2 % 1 != 0:
        return HttpResponse(0)

    ProductRate.objects.update_or_create(customer=request.user, product_id=product_id, defaults={'rate': rate_float})
    return HttpResponse(1)


class ProfileView(View):
    form_class = OrderForm
    template_name = 'profile.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('index')

        form = self.form_class(None)

        all_categories = Category.objects.all()

        try:
            purchases = Product.objects.filter(
                pk__in=Purchase.objects.filter(
                    basket=request.user.baskets.exclude(
                        pk__in=Order.objects.all(). \
                            values('basket_id'))). \
                    values('product_id'))
        except Purchase.DoesNotExist:
            purchases = Product.objects.none

        total = purchases.aggregate(sum=Sum('price'))['sum']

        return render(request, 'profile.html',
                      {'all_categories': all_categories, 'purchases': purchases, 'sum': total, 'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('index')

        basket = request.user.baskets.exclude(pk__in=Order.objects.all().values('basket_id'))

        if not Purchase.objects.filter(
                basket=basket).exists():
            return redirect('profile')

        order = self.form_class(request.POST).save(commit=False)

        order.basket = basket

        order.save()

        return redirect('orders')


def purchase_product(request, product_id):
    if not request.user.is_authenticated or not Product.objects.filter(id=product_id).exists():
        return redirect('index')

    try:
        basket = request.user.baskets.get(order__isnull=True)
    except Basket.DoesNotExist:
        basket = request.user.baskets.create(customer=request.user)

    basket.purchases.create(product_id=product_id)

    return redirect('profile')


def cancel_purchase(request, product_id):
    if not request.user.is_authenticated:
        return redirect('index')

    cursor = connection.cursor()

    cursor.execute('''
    DELETE FROM orders_purchase
    WHERE product_id = %s AND basket_id =
    (SELECT id FROM orders_basket WHERE customer_id = %s AND id NOT IN
    (SELECT basket_id FROM orders_order))
    ''', [product_id, request.user.id])

    connection.commit()

    return redirect('profile')


def orders(request):
    if not request.user.is_authenticated:
        return redirect('index')

    all_categories = Category.objects.all()

    orders = Order.objects.filter(basket__customer=request.user)

    return render(request, 'orders.html', {'all_categories': all_categories, 'orders': orders})


def favorites(request):
    if not request.user.is_authenticated:
        return redirect('index')

    all_categories = Category.objects.all()

    return render(request, 'favorites.html')
