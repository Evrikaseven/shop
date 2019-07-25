
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from main.core.mixins import LoginRolesRequiredMixin
from . import models as _models
from .core.constants import Roles
from . import serializers as _serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from main.roles.zakazschik.views import ZakazschikMainView
from main.roles.zakupschik.views import ZakupschikMainView
from main.roles.administrator.views import AdministratorMainView
from .forms import OrderForm, UserForm


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def __init__(self):
        self.user = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = Roles.ADMINISTRATOR if self.user.is_staff else getattr(self.user, 'role', None)
        context['user_role'] = role

        if role == Roles.ZAKAZSCHIK:
            role_url = ZakazschikMainView.url_name
        elif role == Roles.ZAKUPSCHIK:
            role_url = ZakupschikMainView.url_name
        else:
            role_url = AdministratorMainView.url_name

        context['pers_area_url'] = role_url
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class ProvidersListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/providers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = _models.Provider.objects.all()
        return context


class UsersListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = _models.User.objects.all()
        context['roles'] = Roles
        return context


class UserDetailsView(LoginRolesRequiredMixin, UpdateView):
    template_name = 'main/user_details.html'
    url_name = 'user_details'
    form_class = UserForm
    required_roles = (Roles.UNREGISTERED, Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    model = _models.User

    def get_success_url(self):
        return reverse_lazy('main:user_details', kwargs={'pk': self.kwargs['pk']})


class NewOrderView(LoginRolesRequiredMixin, CreateView):
    template_name = 'main/new_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('main:order_created')
    required_roles = (Roles.ZAKAZSCHIK,)

    def __init__(self):
        self.user = None

    def get_success_url(self):
        return reverse_lazy('main:order_created', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class OrderCreatedView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/order_created.html'
    required_roles = (Roles.ZAKAZSCHIK,)

    def __init__(self):
        self.order_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.order_id
        return context

    def dispatch(self, request, *args, **kwargs):
        self.order_id = kwargs.pop('pk', None)
        return super().dispatch(request, *args, **kwargs)


class OrdersListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/orders.html'
    required_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)

    def __init__(self):
        self.user = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user.role in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            order_qs = _models.Order.objects.get_list()
        else:
            order_qs = _models.Order.objects.get_list(created_by=self.user)
        context['orders'] = order_qs
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class OrderDetailsView(LoginRolesRequiredMixin, UpdateView):
    template_name = 'main/order_details.html'
    url_name = 'order_details'
    form_class = OrderForm
    required_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK)
    model = _models.Order

    def __init__(self):
        self.user = None

    def get_success_url(self):
        return reverse_lazy('main:order_details', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Roles
        context['user_role'] = self.user.role
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class BuyoutsListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/buyouts_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/products_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HelpView(TemplateView):
    template_name = 'main/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Resources
class ProvidersResourceView(LoginRolesRequiredMixin, ModelViewSet):
    queryset = _models.Provider.objects.all()
    serializer_class = _serializers.ProviderSerializer
    permission_classes = (IsAuthenticated,)


class UsersResourceView(LoginRolesRequiredMixin, ModelViewSet):
    queryset = _models.User.objects.all()
    serializer_class = _serializers.UserSerializer
    permission_classes = (IsAuthenticated,)


class OrdersResourceView(LoginRolesRequiredMixin, ModelViewSet):
    queryset = _models.Order.objects.all()
    serializer_class = _serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)
