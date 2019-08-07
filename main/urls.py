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
    path('users/<int:pk>/', main_views.UserDetailsView.as_view(), name=main_views.UserDetailsView.url_name),
    path('products/', main_views.ProductsListView.as_view(), name=main_views.ProductsListView.url_name),
    path('products/new_joint_product/', main_views.NewJointProductView.as_view(), name=main_views.NewJointProductView.url_name),
    path('products/<int:pk>', main_views.UpdateJointProductView.as_view(), name=main_views.UpdateJointProductView.url_name),
    path('buyouts/', main_views.BuyoutsListView.as_view(), name='buyouts'),
    path('help/', main_views.HelpView.as_view(), name='help'),

    # Order related
    path('new_order/', main_views.NewOrderView.as_view(), name='new_order'),
    path('orders/', main_views.OrdersListView.as_view(), name='orders'),
    path('orders/<int:pk>/', main_views.OrderDetailsView.as_view(), name=main_views.OrderDetailsView.url_name),
    path('orders/<int:pk>/paying/', main_views.OrderPayingView.as_view(), name=main_views.OrderPayingView.url_name),
    path('orders/<int:pk>/new_item/', main_views.NewOrderItemView.as_view(), name=main_views.NewOrderItemView.url_name),
    path('orders/<int:pk>/new_joint_item/', main_views.NewJointOrderItemView.as_view(), name=main_views.NewJointOrderItemView.url_name),
    path('order_item/<int:pk>', main_views.OrderItemView.as_view(), name=main_views.OrderItemView.url_name),
    path('order_item/<int:pk>/delete', main_views.DeleteOrderItemView.as_view(), name=main_views.DeleteOrderItemView.url_name),
    path('order_created/<int:pk>', main_views.OrderCreatedView.as_view(), name='order_created'),

    # Django REST framework related
    path('api/', include(router.urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
