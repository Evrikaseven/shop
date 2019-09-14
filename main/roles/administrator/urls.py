from django.urls import path
from .views import AdministratorMainView


urlpatterns = [
    path('', AdministratorMainView.as_view(), name='administrator'),
]
