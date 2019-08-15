from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin


class AdministratorMainView(LoginRolesRequiredViewMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'
