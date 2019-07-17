from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ZakazschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'


class NewOrderView(TemplateView):
    template_name = 'main/new_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
