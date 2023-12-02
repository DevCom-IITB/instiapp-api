from django.conf.urls import url
from django.urls import path
from lostandfound.views import LostandFoundViewset, cso_admin_login
from lostandfound.admin import cso_admin_site


urlpatterns =[
    path('cso_admin_login/', cso_admin_site.urls, name='cso_admin_login'),
    path('products/', LostandFoundViewset.as_view({'get': 'list'}), name='products'),
    path('products/<str:pk>/', LostandFoundViewset.as_view({'get': 'retrieve'}), name='product'),
    path('products/claim/', LostandFoundViewset.as_view({'post': 'claim'}), name='claim'),
]