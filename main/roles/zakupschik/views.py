from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main.models import Order


class ZakupschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    url_name = 'zakupschik'


class ZakupschikIndividualOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik_individual_orders.html'
    url_name = 'zakupschik_individual_orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[''] = Order.objects.filter()


class ZakupschikJointOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik_joint_orders.html'
    url_name = 'zakupschik_joint_orders'


