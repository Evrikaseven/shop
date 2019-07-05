from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main.models import Provider, User


class ZakazschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'


class SborschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/sborschik.html'
    url_name = 'sborschik'


class ZakupschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    url_name = 'zakupschik'


class AdministratorMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = Provider.objects.all()
        context['users'] = User.objects.all()
        return context


