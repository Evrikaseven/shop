from django.urls import path
from .views import (
    ZakazschikMainView,
    ZakupschikMainView,
    SborschikMainView,
    AdministratorMainView,
)


urlpatterns = [
    path('zakazschik/', ZakazschikMainView.as_view(), name='zakazschik'),
    path('zakupschik/', ZakupschikMainView.as_view(), name='zakupschik'),
    path('sborschik/', SborschikMainView.as_view(), name='sborschik'),
    path('administrator/', AdministratorMainView.as_view(), name='administrator'),
]