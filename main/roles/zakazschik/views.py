from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin
from main import models as _models
from main.core.constants import Roles
from django.views.generic.edit import CreateView, UpdateView

from main.forms import OrderForm
from django.urls import reverse_lazy


class ZakazschikMainView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
    required_roles = (Roles.ZAKAZSCHIK,)


class NewOrderView(LoginRolesRequiredMixin, CreateView):
    template_name = 'main/new_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('main:zakazschik')
    required_roles = (Roles.ZAKAZSCHIK,)

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


class OrdersListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/orders.html'
    required_roles = (Roles.ZAKAZSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = _models.Order.objects.all()
        return context


class OrderDetailsView(LoginRolesRequiredMixin, UpdateView):
    template_name = 'main/order_details.html'
    url_name = 'order_details'
    form_class = OrderForm
    required_roles = (Roles.ZAKAZSCHIK,)
    model = _models.Order
    success_url = reverse_lazy('main:zakazschik')

    def __init__(self):
        self.user = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
