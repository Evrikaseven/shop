from django.urls import path
from .views import (
    ZakazschikMainView,
    ZakupschikMainView,
    SborschikMainView,
    AdministratorMainView,
)


urlpatterns = [
    path('zakazschik/', ZakazschikMainView.as_view(), name=ZakazschikMainView.url_name),
    path('zakupschik/', ZakupschikMainView.as_view(), name=ZakupschikMainView.url_name),
    path('sborschik/', SborschikMainView.as_view(), name=SborschikMainView.url_name),
    path('administrator/', AdministratorMainView.as_view(), name=AdministratorMainView.url_name),
]
