
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
from main.core.view_mixins import LoginRolesRequiredViewMixin, LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin
from . import models as _models
from .core.constants import Roles, OrderStatuses
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
)


class IndexView(WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/index.html'

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class ProvidersListView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/providers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = _models.Provider.objects.all()
        return context


class UsersListView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = _models.User.objects.all()
        context['roles'] = Roles
        return context


class UserDetailsView(LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin, UpdateView):
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


class NewOrderView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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
        return context


# class OrderCreatedView(LoginRolesRequiredViewMixin, WithRolesInContextViewMixin, TemplateView):
#     template_name = 'main/to_be_removed__order_created.html'
#     allowed_roles = (Roles.ZAKAZSCHIK,)
#
#     def __init__(self, *args, **kwargs):
#         self.order_id = None
#         super().__init__(*args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['order_id'] = self.order_id
#         return context
#
#     def dispatch(self, request, *args, **kwargs):
#         self.order_id = kwargs.pop('pk', None)
#         return super().dispatch(request, *args, **kwargs)


class OrdersListView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
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


class OrderDetailsView(LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin, UpdateView):
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
        context['user_role'] = self.user.role
        context['user_balance'] = self.object.created_by.balance
        context['roles'] = Roles
        context['order_statuses'] = OrderStatuses
        context['order_statuses_list'] = list(OrderStatuses)
        context['order'] = self.object
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class OrderPayingView(LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin, UpdateView):
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


class NewOrderItemView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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


class NewJointOrderItemView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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


class OrderItemView(LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin, UpdateView):
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
        context['child_order_item'] = getattr(self.object, 'orderitem', None)
        context['product_image'] = self.object.product.image
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_item_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class ReplacementOrderItemView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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


class DeleteOrderItemView(LoginRolesOwnerRequiredUpdateViewMixin, WithLogedUserInContextViewMixin, DeleteView):
    template_name = "main/delete_order_item.html"
    url_name = "delete_order_item"
    allowed_roles = (Roles.ZAKAZSCHIK,)
    model = _models.OrderItem

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.object.order.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        context['order_item'] = self.object
        return context


class CatalogOrderItems(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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


class BuyoutsListView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/buyouts_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsListView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/products_list.html'
    url_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = _models.Product.objects.get_joint_products()
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class ProductsAddToOrderView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, FormView):
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


class NewJointProductView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, CreateView):
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


class UpdateJointProductView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, UpdateView):
    template_name = 'main/new_joint_product.html'
    url_name = 'update_joint_product'
    form_class = ProductForm
    model = _models.Product
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


class HelpView(WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/help.html'


# Resources
class ProvidersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.Provider.objects.all()
    serializer_class = _serializers.ProviderSerializer
    permission_classes = (IsAuthenticated,)


class UsersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.User.objects.all()
    serializer_class = _serializers.UserSerializer
    permission_classes = (IsAuthenticated,)


class OrdersResourceView(LoginRolesRequiredViewMixin, ModelViewSet):
    queryset = _models.Order.objects.all()
    serializer_class = _serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)
