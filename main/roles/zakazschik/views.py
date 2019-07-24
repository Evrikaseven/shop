from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin
from main.core.constants import Roles


class ZakazschikMainView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
    required_roles = (Roles.ZAKAZSCHIK,)


