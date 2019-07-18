from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main import models as _models
from django.views.generic.edit import CreateView

from main.forms import OrderForm, ProviderForm
from django.urls import reverse_lazy


class ZakazschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'


class NewOrderView(CreateView):
    template_name = 'main/new_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('main:zakazschik')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class OrdersListView(TemplateView):
    template_name = 'main/orders_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = _models.Order.objects.all()
        return context
