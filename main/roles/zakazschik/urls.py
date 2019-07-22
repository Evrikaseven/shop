from django.urls import path
from .views import *


urlpatterns = [
    path('', ZakazschikMainView.as_view(), name=ZakazschikMainView.url_name),
    path('new_order/', NewOrderView.as_view(), name='new_order'),
    path('orders/', OrdersListView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailsView.as_view(), name=OrderDetailsView.url_name),
]
