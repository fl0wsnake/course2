from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  url(r'^product/(?P<product_id>[0-9]+)$', views.product_info, name='product_info'),
                  url(r'^purchase/(?P<product_id>[0-9]+)$', views.purchase_product, name='purchase_product')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
