from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, CommonContextViewMixin


class AdministratorMainView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/administrator.html'
    url_name = 'administrator'
