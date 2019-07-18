
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models as _models
from . import serializers as _serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from main.roles.zakazschik.views import ZakazschikMainView
from main.roles.zakupschik.views import ZakupschikMainView
from main.roles.sborschik.views import SborschikMainView
from main.roles.administrator.views import AdministratorMainView
from .forms import OrderForm


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def __init__(self):
        self.user = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = _models.Roles.ADMINISTRATOR if self.user.is_staff else getattr(self.user, 'role', None)
        context['user_role'] = role

        if role == _models.Roles.ZAKAZSCHIK:
            role_url = ZakazschikMainView.url_name
        elif role == _models.Roles.ZAKUPSCHIK:
            role_url = ZakupschikMainView.url_name
        elif role == _models.Roles.SBORSCHIK:
            role_url = SborschikMainView.url_name
        else:
            role_url = AdministratorMainView.url_name

        context['pers_area_url'] = role_url
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)


class ProvidersListView(LoginRequiredMixin, TemplateView):
    template_name = 'main/providers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = _models.Provider.objects.all()
        return context


class UsersListView(LoginRequiredMixin, TemplateView):
    template_name = 'main/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = _models.User.objects.all()
        return context


class OrdersListView(TemplateView):
    template_name = 'main/orders_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrderCreateView(CreateView):
    template_name = 'main/order_details.html'
    form_class = OrderForm
    success_url = '/order_details/'

    def __init__(self):
        self.user = None

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


class BuyoutsListView(TemplateView):
    template_name = 'main/buyouts_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductsListView(TemplateView):
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
class ProvidersResourceView(ModelViewSet):
    queryset = _models.Provider.objects.all()
    serializer_class = _serializers.ProviderSerializer
    permission_classes = (IsAuthenticated,)


class UsersResourceView(ModelViewSet):
    queryset = _models.User.objects.all()
    serializer_class = _serializers.UserSerializer
    permission_classes = (IsAuthenticated,)


class OrdersResourceView(ModelViewSet):
    queryset = _models.Order.objects.all()
    serializer_class = _serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)
