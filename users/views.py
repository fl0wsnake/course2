from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout


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


# class LoginFormView(View):
#     form_class = LoginForm
#     template_name = 'login.html'
#
#     def get(self, request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request):
#         form = self.form_class(request.POST)
#
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('index')
#
#         return render(request, self.template_name, {'form': form})
#
#
# def user_logout(request):
#     logout(request)
#     return redirect('index')
