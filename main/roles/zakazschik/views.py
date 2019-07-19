from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin
from main import models as _models
from main.core.constants import Roles
from django.views.generic.edit import CreateView

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class OrdersListView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/orders_list.html'
    required_roles = (Roles.ZAKAZSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = _models.Order.objects.all()
        return context
