from django.urls import path
from .views import *


urlpatterns = [
    path('', ZakazschikMainView.as_view(), name=ZakazschikMainView.url_name),
]
