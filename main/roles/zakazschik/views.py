from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, WithRolesInContextViewMixin
from main.core.constants import Roles
from .fetchers import ZakazschikFetcher


class ZakazschikMainView(LoginRolesRequiredViewMixin, WithRolesInContextViewMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
    allowed_roles = (Roles.ZAKAZSCHIK,)

