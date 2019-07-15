from django.urls import path
from .views import SborschikMainView


urlpatterns = [
    path('main/', SborschikMainView.as_view(), name=SborschikMainView.url_name),
]

