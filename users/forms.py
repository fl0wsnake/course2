from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


# class LoginForm(AuthenticationForm):
#     # password = forms.CharField(widget=forms.PasswordInput)
#     #
#     # class Meta:
#     #     model = User
#     #     fields = ['username', 'password']
#     username = forms.CharField(label="Username", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
#     password = forms.CharField(label="Password", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))