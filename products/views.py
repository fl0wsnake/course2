from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Category


def index(request):
    all_categories = Category.objects.select_related().all()
    return render(request, 'index.html', {'all_categories': all_categories})
    # t = loader.get_template('index.html')
    # c = {'all_categories': all_categories}
    # return HttpResponse(t.render(c, request), content_type='application/xhtml+xml')
    # return HttpResponse("12345")
