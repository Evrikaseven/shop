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
    path('users/<int:pk>/', main_views.UserDetailsView.as_view(), name='user_details'),
    path('products/', main_views.ProductsListView.as_view(), name='products'),
    path('products/<int:pk>/add_to_order/', main_views.ProductsAddToOrderView.as_view(), name='details'),
    path('products/<int:pk>/add_to_order/<int:order_pk>', main_views.ProductsAddToOrderView.as_view(), name='details'),
    path('products/new_joint_product/', main_views.NewJointProductView.as_view(), name='new_joint_product'),
    path('products/<int:pk>', main_views.UpdateJointProductView.as_view(), name='update_joint_product'),
    path('products/<int:pk>/delete/', main_views.DeleteProductView.as_view(), name='delete_product'),
    path('buyouts/', main_views.BuyoutsListView.as_view(), name='buyouts'),
    path('help/', main_views.HelpView.as_view(), name='help'),
    path('news/', main_views.NewsView.as_view(), name='news'),

    # Order related
    path('new_order/', main_views.NewOrderView.as_view(), name='new_order'),
    path('orders/', main_views.OrdersListView.as_view(), name='orders'),
    path('orders/product_to_order/<int:product_id>', main_views.OrdersListView.as_view(), name='product_to_orders'),
    path('orders/<int:pk>/', main_views.OrderDetailsView.as_view(), name='order_details'),
    path('orders/<int:pk>/pay_done/', main_views.OrderPayingView.as_view(), name='order_paying'),
    path('orders/<int:pk>/new_item/', main_views.NewOrderItemView.as_view(), name='new_order_item'),
    path('orders/<int:pk>/new_joint_item/', main_views.NewJointOrderItemView.as_view(), name='new_joint_order_item'),

    path('orders/joint_item_to_product/<int:product_pk>', main_views.NewJointOrderItemView.as_view(),
         name='joint_item_to_product_new_order'),
    path('orders/<int:pk>/joint_item_to_product/<int:product_pk>', main_views.NewJointOrderItemView.as_view(),
         name='joint_item_to_product'),

    path('order_item/<int:pk>', main_views.OrderItemView.as_view(), name='order_item_details'),
    path('order_item/<int:pk>/new_replacement/', main_views.ReplacementOrderItemView.as_view(),
         name='replacement_order_item'),
    path('order_item/<int:pk>/delete/', main_views.DeleteOrderItemView.as_view(), name='delete_order_item'),

    # Catalog items
    path('catalog/', main_views.CatalogOrderItems.as_view(), name='catalog'),
    path('catalog/<int:pk>/', main_views.CatalogOrderItems.as_view(), name='catalog'),

    # Check image
    path('orders/<int:pk>/paying/', main_views.JointReceiptForOrderView.as_view(), name='receipt_for_order'),

    path('settings/', main_views.SettingsView.as_view(), name='settings'),

    # Django REST framework related
    path('api/', include(router.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
