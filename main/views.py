
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.views.generic.list import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from main.core.view_mixins import (
    LoginRolesRequiredViewMixin,
    LoginRolesOwnerRequiredUpdateViewMixin,
    CommonContextViewMixin,
    OrderCreateStatusOnlyAllowUpdateViewMixin,
)
from . import models as _models
from .core.constants import (
    Roles,
    OrderStatuses,
    ShoppingTypes,
    DeliveryTypes,
    DELIVERY_PRICES,
    OrderItemStatuses,
    PurchaseAndDeliveryTypes,
)
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
    ProviderForm,
    NewsForm,
)


class IndexView(CommonContextViewMixin, TemplateView):
    template_name = 'main/index.html'

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement'] = _models.SettingOptionHandler('announcement').value
        context['contacts'] = _models.SettingOptionHandler('contacts').value
        context['partnership'] = _models.SettingOptionHandler('partnership').value
        context['work_schedule'] = _models.SettingOptionHandler('work_schedule').value
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class ProvidersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/providers_list.html'
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    form_class = ProviderForm
    model = _models.Provider
    success_url = reverse_lazy('main:providers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = _models.Provider.objects.all()
        return context


class UsersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, ListView):
    template_name = 'main/users_list.html'
    paginate_by = 20

    def get_queryset(self):
        return _models.User.objects.all() if self.user.is_superuser else _models.User.objects.get_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Roles
        return context


class UserDetailsView(LoginRolesOwnerRequiredUpdateViewMixin, CommonContextViewMixin, SuccessMessageMixin, UpdateView):
    template_name = 'main/user_details.html'
    form_class = UserForm
    allowed_roles = (Roles.UNREGISTERED, Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    model = _models.User
    success_message = 'Настройки сохранены'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('main:user_details', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles_list'] = list(Roles)
        context['balance_update_allowed'] = self.user.role == Roles.ADMINISTRATOR
        return context


class DeleteUserView(LoginRolesOwnerRequiredUpdateViewMixin, CommonContextViewMixin, DeleteView):
    template_name = "main/delete_user.html"
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    model = _models.User

    def get_success_url(self):
        return reverse_lazy('main:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_delete'] = self.object
        return context


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


class OrdersListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, ListView):
    template_name = 'main/orders.html'
    paginate_by = 20
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.product_id = None
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.user.role in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            order_qs = _models.Order.objects.get_list()
        elif self.product_id:
            order_qs = _models.Order.objects.get_list(created_by=self.user, status=OrderStatuses.CREATED)
        else:
            order_qs = _models.Order.objects.get_list(created_by=self.user)
        return order_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_statuses'] = OrderStatuses

        if self.product_id:
            context['product_id'] = self.product_id
        return context

    def dispatch(self, request, *args, **kwargs):
        if 'product_id' in kwargs:
            self.product_id = kwargs['product_id']
        return super().dispatch(request, *args, **kwargs)


class OrderDetailsView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, SuccessMessageMixin, UpdateView):
    template_name = 'main/order_details.html'
    form_class = OrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    allowed_non_owner_roles = (Roles.ZAKUPSCHIK, )
    model = _models.Order
    success_message = 'Настройки сохранены'

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
        context['receipts'] = _models.Receipt.objects.filter(order=self.object.id)
        context['extra_charge'] = _models.SettingOptionHandler('extra_charge').value
        return context


class OrderPayingView(LoginRolesOwnerRequiredUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/order_paying.html'
    form_class = OrderForm
    allowed_roles = (Roles.ZAKAZSCHIK,)
    allowed_non_owner_roles = (Roles.ZAKAZSCHIK,)
    model = _models.Order


class JointReceiptForOrderView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/receipt_for_order.html'
    form_class = ReceiptForOrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self):
        self.user = None
        self.order = None

    def get_success_url(self):
        return reverse_lazy('main:order_paying', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order.pk
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        order_id = kwargs['pk']
        self.order = _models.Order.objects.get(id=order_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.order.pay_order()
        return super().form_valid(form)


class NewOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_order_item.html'
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
        context['order'] = _models.Order.objects.get(id=self.order_id)
        context['order_items_statuses_list'] = list(OrderItemStatuses)
        context['purchase_and_delivery_types_list'] = list(PurchaseAndDeliveryTypes)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class NewJointOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_joint_order_item.html'
    form_class = JointItemToOrderForm
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        self.product_id = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        if not self.order_id:
            self.order_id = self.object.order.id
        return reverse_lazy('main:order_details', kwargs={'pk': self.order_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_id'] = self.order_id
        kwargs['product_id'] = self.product_id
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = _models.Product.objects.get(id=self.product_id)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs.get('pk')
        self.product_id = kwargs['product_pk']
        return super().dispatch(request, *args, **kwargs)


class OrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/order_item_details.html'
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
        context['child_order_item'] = getattr(self.object, 'replacement', None)
        context['product_image'] = self.object.product.image
        context['order_items_statuses_list'] = list(OrderItemStatuses)
        context['purchase_and_delivery_types_list'] = list(PurchaseAndDeliveryTypes)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_item_id = kwargs['pk']
        return super().dispatch(request, *args, **kwargs)


class ReplacementOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/new_order_item.html'
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
        context['order'] = self.order_item.order
        context['order_items_statuses_list'] = list(OrderItemStatuses)
        context['purchase_and_delivery_types_list'] = list(PurchaseAndDeliveryTypes)
        return context

    def dispatch(self, request, *args, **kwargs):
        order_item_pk = kwargs['pk']
        self.order_item = _models.OrderItem.objects.get(pk=order_item_pk)
        return super().dispatch(request, *args, **kwargs)


class DeleteOrderItemView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, DeleteView):
    template_name = "main/delete_order_item.html"
    allowed_roles = (Roles.ZAKAZSCHIK,)
    model = _models.OrderItem

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.object.order.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_item'] = self.object
        return context

    def post(self, *args, **kwargs):
        try:
            order_item = _models.OrderItem.objects.get(pk=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return self.handle_no_permission()
        if (self.user.role == Roles.ZAKAZSCHIK and
                order_item.product.shopping_type == ShoppingTypes.JOINT and
                order_item.product.quantity == 0):
            return self.handle_no_permission()
        return super().post(*args, **kwargs)


class DeleteOrderView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, DeleteView):
    template_name = "main/delete_order.html"
    allowed_roles = (Roles.ZAKAZSCHIK, Roles.ADMINISTRATOR)
    model = _models.Order
    permission_denied_message = 'Заказ может быть удален только в момент создания или когда закрыт'

    def get_success_url(self):
        return reverse_lazy('main:orders')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object
        return context

    def post(self, *args, **kwargs):
        order_id = kwargs['pk']
        order_status = _models.Order.objects.get(pk=order_id).status
        if order_status != OrderStatuses.CREATED:
            return self.handle_no_permission()
        return super().post(*args, **kwargs)


class DeleteProductView(OrderCreateStatusOnlyAllowUpdateViewMixin, CommonContextViewMixin, DeleteView):
    template_name = "main/delete_product.html"
    # allowed_roles = () Admin only is allowed
    model = _models.Product

    def get_success_url(self):
        return reverse_lazy('main:products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object
        return context


class CatalogOrderItems(LoginRolesRequiredViewMixin, CommonContextViewMixin, ListView):
    template_name = 'main/catalog_items.html'
    form_class = ProductForm
    model = _models.Product
    allowed_roles = (Roles.ZAKAZSCHIK,)

    def __init__(self, *args, **kwargs):
        self.order_id = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = _models.Product.objects.get_joint_products()
        context['order'] = _models.Order.objects.get(pk=self.order_id) if self.order_id else None
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs.pop('pk', None)
        return super().dispatch(request, *args, **kwargs)


class BuyoutsListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/buyouts_list.html'


class ProductsListView(LoginRolesRequiredViewMixin, CommonContextViewMixin, ListView):
    template_name = 'main/products_list.html'
    paginate_by = 10

    def get_queryset(self):
        return _models.Product.objects.get_joint_products()


class ProductsAddToOrderView(LoginRolesRequiredViewMixin, CommonContextViewMixin, FormView):
    template_name = 'main/products_add.html'
    allowed_roles = (Roles.ZAKAZSCHIK,)
    model = _models.Product
    form_class = ProductForm

    def __init__(self, *args, **kwargs):
        self.product_id = None
        self.order_id = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = _models.Product.objects.get(id=self.product_id)
        context['order'] = _models.Order.objects.get(id=self.order_id) if self.order_id else None
        return context

    def dispatch(self, request, *args, **kwargs):
        self.product_id = kwargs['pk']
        self.order_id = kwargs.get('order_pk', None)
        return super().dispatch(request, *args, **kwargs)


class NewJointProductView(LoginRolesRequiredViewMixin, CommonContextViewMixin, CreateView):
    template_name = 'main/product_details.html'
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


class UpdateProductView(LoginRolesRequiredViewMixin, CommonContextViewMixin, UpdateView):
    template_name = 'main/product_details.html'
    form_class = ProductForm
    model = _models.Product
    allowed_roles = (Roles.ZAKUPSCHIK, )

    def get_success_url(self):
        return reverse_lazy('main:products')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HelpView(CommonContextViewMixin, TemplateView):
    template_name = 'main/help.html'


class NewsView(CommonContextViewMixin, TemplateView):
    template_name = 'main/news.html'
    form_class = NewsForm
    models = _models.News

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news'] = _models.News.objects.all()
        return context


class EditNewsView(LoginRolesRequiredViewMixin, CommonContextViewMixin, FormView):
    template_name = 'main/edit_news.html'
    form_class = NewsForm

    def get_success_url(self):
        return reverse_lazy('main:edit_news')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news'] = _models.News.objects.all()
        return context


class SettingsView(LoginRolesRequiredViewMixin, CommonContextViewMixin, SuccessMessageMixin, FormView):
    template_name = 'main/settings.html'
    form_class = SettingsForm
    success_message = 'Настройки сохранены'

    def get_success_url(self):
        return reverse_lazy('main:settings')

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
