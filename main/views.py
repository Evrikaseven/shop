
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
from main.core.view_mixins import (
    LoginRolesRequiredViewMixin,
    LoginRolesOwnerRequiredUpdateViewMixin,
    CommonContextViewMixin,
    OrderCreateStatusOnlyAllowUpdateViewMixin,
)
from . import models as _models
from .core.constants import Roles, OrderStatuses, ShoppingTypes, DeliveryTypes, DELIVERY_PRICES
from . import serializers as _serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .forms import (
    NewOrderForm,
    OrderForm,
    UserForm,
    OrderItemForm,
    JointItemToOrderForm,
    ProductForm,
    SettingsForm,
    ReceiptForOrderForm,
)


class IndexView(CommonContextViewMixin, TemplateView):
    template_name = 'main/index.html'

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement'] = _models.SettingOptionHandler('announcement').value
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class ProvidersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/providers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = _models.Provider.objects.all()
        return context


class UsersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = _models.User.objects.all() if self.user.is_superuser else _models.User.objects.get_list()
        context['roles'] = Roles
        return context


class UserDetailsView(LoginRolesOwnerRequiredUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/user_details.html'
    url_name = 'user_details'
    form_class = UserForm
    allowed_roles = (Roles.UNREGISTERED, Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    model = _models.User

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('main:user_details', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NewOrderView(LoginRolesRequiredViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_order.html'
    form_class = NewOrderForm
    allowed_roles = (Roles.ZAKAZSCHIK,)

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['STATUS_CREATED_STR'] = OrderStatuses.CREATED_STR
        return context


class OrdersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/orders.html'
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.product_id = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.product_id:
            context['product_id'] = self.product_id

        if self.user.role in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            order_qs = _models.Order.objects.get_list()
        elif self.product_id:
            order_qs = _models.Order.objects.get_list(created_by=self.user, status=OrderStatuses.CREATED)
        else:
            order_qs = _models.Order.objects.get_list(created_by=self.user)
        context['orders'] = order_qs
        return context

    def dispatch(self, request, *args, **kwargs):
        if 'product_id' in kwargs:
            self.product_id = kwargs['product_id']
        return super().dispatch(request, *args, **kwargs)


class OrderDetailsView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/order_details.html'
    url_name = 'order_details'
    form_class = OrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    allowed_non_owner_roles = (Roles.ZAKUPSCHIK, )
    model = _models.Order

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_is_allowed'] = (self.user.role == Roles.ADMINISTRATOR or
                                        (self.user.role == Roles.ZAKAZSCHIK and
                                         self.object.status == OrderStatuses.CREATED))
        context['user_role'] = self.user.role
        context['user_balance'] = self.object.created_by.balance
        context['roles'] = Roles
        context['order_statuses'] = OrderStatuses
        context['order_statuses_list'] = list(OrderStatuses)
        delivery_prices = dict(DELIVERY_PRICES)
        context['delivery_types_list'] = [(delivery[0], '{} - {} руб.'.format(delivery[1], delivery_prices[delivery[0]]))
                                          for delivery in DeliveryTypes]
        context['show_delivery_address'] = self.object.delivery in (DeliveryTypes.TK,
                                                                    DeliveryTypes.HOME_DELIVERY,
                                                                    DeliveryTypes.POST_MAIL)
        context['order'] = self.object
        context['SHOPPING_TYPES'] = ShoppingTypes
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class OrderPayingView(LoginRolesOwnerRequiredUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/order_paying.html'
    form_class = OrderForm
    allowed_roles = (Roles.ZAKAZSCHIK,)
    allowed_non_owner_roles = (Roles.ZAKAZSCHIK,)
    url_name = 'order_paying'
    model = _models.Order

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        form.pay_order()
        return context


class JointReceiptForOrderView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/receipt_for_order.html'
    url_name = 'receipt_for_order'
    form_class = ReceiptForOrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self):
        self.user = None
        self.order_id = None

    def get_success_url(self):
        return reverse_lazy('main:order_paying', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order_id
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['order'] = _models.Order.objects.get(id=self.order_id)
        # context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.order_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class NewOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_order_item.html'
    url_name = 'new_order_item'
    form_class = OrderItemForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order_id
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['order'] = _models.Order.objects.get(id=self.order_id)
        # context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class NewJointOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_joint_order_item.html'
    #url_name = 'new_joint_order_item'
    form_class = JointItemToOrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        self.product_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order_id
        kwargs['product_id'] = self.product_id
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['order'] = _models.Order.objects.get(id=self.order_id)
        # context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs['pk']
        self.product_id = kwargs['product_pk']
        return super().dispatch(request, *args, **kwargs)


class OrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/order_item_details.html'
    url_name = 'order_item_details'
    form_class = OrderItemForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    allowed_non_owner_roles = (Roles.ZAKUPSCHIK,)
    model = _models.OrderItem

    def __init__(self, *args, **kwargs):
        self.order_item_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        if self.user.role == Roles.ZAKUPSCHIK:
            return reverse_lazy('main:order_item_details', kwargs={'pk': self.object.id})
        return reverse_lazy('main:order_details', kwargs={'pk': self.object.order.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.object.order.id
        kwargs['user'] = self.user
        kwargs['is_image_update_forbidden'] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_item'] = self.object
        context['SHOPPING_TYPES'] = ShoppingTypes
        context['child_order_item'] = getattr(self.object, 'orderitem', None)
        context['product_image'] = self.object.product.image
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_item_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class ReplacementOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_order_item.html'
    url_name = 'replacement_order_item'
    form_class = OrderItemForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.order_item = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.order_item.order.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order_item.order.id
        kwargs['user'] = self.user
        # kwargs['is_image_update_forbidden'] = True
        kwargs['parent_item'] = self.order_item
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_image'] = self.order_item.product.image
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        order_item_pk = kwargs['pk']
        self.order_item = _models.OrderItem.objects.get(pk=order_item_pk)
        return super().dispatch(request, *args, **kwargs)


class DeleteOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, DeleteView):
    template_name = "main/delete_order_item.html"
    url_name = "delete_order_item"
    allowed_roles = (Roles.ZAKAZSCHIK,)
    model = _models.OrderItem

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.object.order.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.object.order.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        context['order_item'] = self.object
        return context


class CatalogOrderItems(LoginRolesRequiredViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/catalog_items.html'
    url_name = 'catalog'
    form_class = ProductForm
    model = _models.Product
    allowed_roles = (Roles.ZAKAZSCHIK,)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:main_views.ProductsDetailsView.url_name', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = _models.Product.objects.get_joint_products()
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs.pop('pk', None)
        return super().dispatch(request, *args, **kwargs)


class BuyoutsListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/buyouts_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/products_list.html'
    url_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = _models.Product.objects.get_joint_products()
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class ProductsAddToOrderView(LoginRolesRequiredViewMixin, CommonContextViewMixin, FormView):
    template_name = 'main/products_add.html'
    url_name = 'details'
    allowed_roles = (Roles.ZAKAZSCHIK,)
    model = _models.Product
    form_class = ProductForm

    def __init__(self, *args, **kwargs):
        self.product_id = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = _models.Product.objects.get(id=self.product_id)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.product_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class NewJointProductView(LoginRolesRequiredViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_joint_product.html'
    url_name = 'new_joint_product'
    form_class = ProductForm
    # allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:products')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs


class UpdateJointProductView(LoginRolesRequiredViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/new_joint_product.html'
    url_name = 'update_joint_product'
    form_class = ProductForm
    model = _models.Product
    # allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def get_success_url(self):
        return reverse_lazy('main:products')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs


class HelpView(CommonContextViewMixin, TemplateView):
    template_name = 'main/help.html'


class SettingsView(LoginRolesRequiredViewMixin, CommonContextViewMixin, FormView):
    template_name = 'main/settings.html'
    form_class = SettingsForm
    url_name = 'settings'

    def get_success_url(self):
        return reverse_lazy('main:administrator')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# Resources
class ProvidersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.Provider.objects.all()
    serializer_class = _serializers.ProviderSerializer
    permission_classes = (IsAuthenticated,)


class UsersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.User.objects.get_list()
    serializer_class = _serializers.UserSerializer
    permission_classes = (IsAuthenticated,)


class OrdersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.Order.objects.all()
    serializer_class = _serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)
