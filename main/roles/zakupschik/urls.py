from django.urls import path, re_path
import main.roles.zakupschik.views as views

urlpatterns = [
    path('', views.ZakupschikMainView.as_view(), name='zakupschik'),
    path('locations/', views.ZakupschikLocationsView.as_view(), name='zakupschik_locations'),
    re_path(r'^locations/places/(?P<place>[0-9/\-\w]+)/$', views.ZakupschikOrderItemsByPlaceView.as_view(), name='zakupschik_order_details_by_place'),
    re_path('locations/(?P<location>[0-9/\w]+)/(?P<floor>[0-9/\w]+)/(?P<line>[0-9/\w]+)/$', views.ZakupschikPlacesView.as_view(), name='zakupschik_places'),
    re_path('locations/(?P<location>[0-9/\w]+)/(?P<floor>[0-9/\w]+)/$', views.ZakupschikLocationsLinesView.as_view(), name='zakupschik_locations_lines'),
    re_path('locations/(?P<location>[0-9/\w]+)/$', views.ZakupschikLocationsFloorsView.as_view(), name='zakupschik_locations_floors'),
    path('products_to_deliver/', views.ZakupschikUsersWithProductsToDeliverView.as_view(), name='zakupschik_products_ready_to_delivery'),
]
