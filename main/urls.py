from django.urls import path, include
from . import views as main_views
from .roles import urls as roles_urls
from .accounts import urls as accounts_urls

app_name = 'main'

urlpatterns = [
    path('', main_views.IndexView.as_view(), name='index'),
    path('roles/', include(roles_urls)),
    path('accounts/', include(accounts_urls)),
    path('providers/', main_views.ProvidersListView.as_view(), name='providers'),
    path('users/', main_views.UsersListView.as_view(), name='users'),
    path('orders/', main_views.OrdersListView.as_view(), name='orders'),
    path('products/', main_views.ProductsListView.as_view(), name='products'),
    path('buyouts/', main_views.BuyoutsListView.as_view(), name='buyouts'),
    path('help/', main_views.HelpView.as_view(), name='help'),
]
