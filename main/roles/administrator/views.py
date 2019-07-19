from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin


class AdministratorMainView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'
