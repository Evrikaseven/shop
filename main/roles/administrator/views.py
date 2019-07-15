from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class AdministratorMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'
