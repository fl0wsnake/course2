from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^product/(?P<product_id>[0-9]+)$', views.product_info, name='product_info'),
    url(r'^subcategory/(?P<subcategory_name>[a-zA-Z]+)$', views.subcategory_products,
        name='subcategory_products'),
    url(r'^add_product$', views.AddProductView.as_view(), name='add_product'),
    url(r'^statistics$', views.statistics, name='statistics'),
    url(r'^statistics/(?P<subcategory_name>[a-zA-Z]+)$', views.subcategory_manufacturer_stat, name='subcategory_manufacturer_stat'),
    url(r'^categories_cost_report$', views.categories_cost_report, name='categories_cost_report'),
    url(r'^categories_amount_report$', views.categories_amount_report, name='categories_amount_report')
]
