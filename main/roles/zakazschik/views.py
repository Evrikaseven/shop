from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin, WithRolesInContextMixin
from main.core.constants import Roles
from .fetchers import ZakazschikFetcher


class ZakazschikMainView(LoginRolesRequiredMixin, WithRolesInContextMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
    allowed_roles = (Roles.ZAKAZSCHIK,)

