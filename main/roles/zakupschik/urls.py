from django.urls import path
import main.roles.zakupschik.views as views


urlpatterns = [
    path('', views.ZakupschikMainView.as_view(), name=views.ZakupschikMainView.url_name),
    path('orders/', views.ZakupschikOrdersPlacesView.as_view(),
         name=views.ZakupschikOrdersPlacesView.url_name),
    path('orders/<slug:place>/', views.ZakupschikOrdersByPlacesView.as_view(),
         name=views.ZakupschikOrdersByPlacesView.url_name),
]