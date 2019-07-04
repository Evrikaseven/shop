from django.urls import path, include
from .views import IndexView
from .roles import urls as roles_urls
from .accounts import urls as accounts_urls

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('', include(roles_urls)),
    path('', include(accounts_urls)),
]