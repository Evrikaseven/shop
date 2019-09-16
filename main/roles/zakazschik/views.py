from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, CommonContextViewMixin
from main.core.constants import Roles


class ZakazschikMainView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    allowed_roles = (Roles.ZAKAZSCHIK,)
