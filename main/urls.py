from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as main_views
from .roles import urls as roles_urls
from .accounts import urls as accounts_urls
from rest_framework.routers import DefaultRouter

app_name = 'main'


router = DefaultRouter()
router.register('users', main_views.UsersResourceView)
router.register('orders', main_views.OrdersResourceView)
router.register('providers', main_views.ProvidersResourceView)


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

    path('api/', include(router.urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
