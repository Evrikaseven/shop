from django.urls import path
from .views import *


urlpatterns = [
    path('main/', ZakazschikMainView.as_view(), name=ZakazschikMainView.url_name),
    path('new_order/', NewOrderView.as_view(), name='new_order'),
    path('orders_list/', OrdersListView.as_view(), name='orders_list'),
]
