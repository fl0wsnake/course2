from django.conf.urls import url
from . import views

urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  url(r'^product/(?P<product_id>[0-9]+)$', views.product_info, name='product_info'),
                  url(r'^subcategory/(?P<subcategory_name>[a-zA-Z]+)$', views.subcategory_products,
                      name='subcategory_products'),
                  url(r'^purchase/(?P<product_id>[0-9]+)$', views.purchase_product, name='purchase_product')
              ]
