from django.urls import path
from .views import AdministratorMainView


urlpatterns = [
    path('main/', AdministratorMainView.as_view(), name=AdministratorMainView.url_name),
]

