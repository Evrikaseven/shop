
from django.views.generic.base import TemplateView
from .models import Roles
from main.roles import views as roles_views


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def __init__(self):
        self.user = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = Roles.ADMINISTRATOR if self.user.is_staff else getattr(self.user, 'role', None)
        context['user_role'] = role

        if role == Roles.ZAKAZSCHIK:
            role_url = roles_views.ZakazschikMainView.url_name
        elif role == Roles.ZAKUPSCHIK:
            role_url = roles_views.ZakupschikMainView.url_name
        elif role == Roles.SBORSCHIK:
            role_url = roles_views.SborschikMainView.url_name
        else:
            role_url = roles_views.AdministratorMainView.url_name

        context['pers_area_url'] = role_url
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)



