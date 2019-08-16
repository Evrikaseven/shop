from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin


class AdministratorMainView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'
