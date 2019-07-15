from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ZakazschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
