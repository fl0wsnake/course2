from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .forms import RegisterForm
from django.contrib.auth import login
from .models import *
from django.http import HttpResponse
from orders.models import *
from products.models import Product


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


def profile(request):
    if not request.user.is_authenticated:
        return redirect('index')

    try:
        products = request.user.baskets.get(customer=request.user).purchases.select_related('product')
    except Purchase.DoesNotExist:
        products = Purchase.objects.none

    return render(request, 'profile.html', {'products': products})


def orders(request):
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'orders.html')


def favorites(request):
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'favorites.html')


def purchase_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('index')

    product = get_object_or_404(Product, id=product_id)

    try:
        basket = request.user.baskets.get(order__isnull=True)
    except Basket.DoesNotExist:
        basket = request.user.baskets.create(customer=request.user)

    basket.purchases.create(product_id=product_id)

    return redirect('profile')




























