from django.urls import path
from .views import ZakazschikMainView


urlpatterns = [
    path('', ZakazschikMainView.as_view(), name='zakazschik'),
]
