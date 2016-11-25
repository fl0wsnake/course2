from django.shortcuts import render
from .models import *

def getAllCategories(request):
    allCategories = Category.objects.all()
    context = {'allCategories', allCategories}

