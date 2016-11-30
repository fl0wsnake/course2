from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  url(r'products/(?P<product_id>[0-9]+)', views.product_info, name='product_info')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
