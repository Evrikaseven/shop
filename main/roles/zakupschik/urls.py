from django.urls import path
import main.roles.zakupschik.views as views


urlpatterns = [
    path('', views.ZakupschikMainView.as_view(), name='zakupschik'),
    path('orders/', views.ZakupschikOrdersPlacesView.as_view(), name='zakupschik_orders_places'),
    path('products_to_deliver/', views.ZakupschikUsersWithProductsToDeliverView.as_view(), name='zakupschik_products_ready_to_delivery'),
    path('orders/<slug:place>/', views.ZakupschikOrdersByPlacesView.as_view(), name='zakupschik_order_details_by_place'),
]