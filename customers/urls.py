from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterFormView.as_view(), name='register'),
    url(r'^like/(?P<product_id>[0-9]+)$', views.like_product, name='like'),
    url(r'^rate/(?P<product_id>[0-9]+)/(?P<rate>[0-9]+(?:\.[5])?)$', views.rate_product, name='rate'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/favorites/$', views.profile, name='favorites'),
    url(r'^profile/orders/$', views.profile, name='orders'),
    url(r'^purchase/(?P<product_id>[0-9]+)$', views.purchase_product, name='purchase_product'),
]
