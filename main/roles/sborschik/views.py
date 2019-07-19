from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin
from main.core.constants import Roles


class SborschikMainView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/sborschik.html'
    required_roles = (Roles.SBORSCHIK,)
    url_name = 'sborschik'
