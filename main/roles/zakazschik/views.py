from django.views.generic.base import TemplateView
from main.core.mixins import LoginRolesRequiredMixin
from main.core.constants import Roles
from .fetchers import ZakazschikFetcher


class ZakazschikMainView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/zakazschik.html'
    url_name = 'zakazschik'
    allowed_roles = (Roles.ZAKAZSCHIK,)


class ZakazschikOrdersByIdView(LoginRolesRequiredMixin, TemplateView):
    template_name = 'main/order_details.html'
    url_name = 'order_details'
    allowed_roles = (Roles.ZAKAZSCHIK,)

    def __init__(self):
        self.place = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakazschikFetcher()
        context['orders'] = fetcher.orders_by_id(self.id)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.id = kwargs.pop('id', None)
        return super().dispatch(request, *args, **kwargs)
