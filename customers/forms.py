from django.contrib.auth.models import User
from orders.models import Order
from django import forms


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['status']