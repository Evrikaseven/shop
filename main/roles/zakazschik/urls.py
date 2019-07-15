from django.urls import path
from .views import ZakazschikMainView


urlpatterns = [
    path('main/', ZakazschikMainView.as_view(), name=ZakazschikMainView.url_name),
]
