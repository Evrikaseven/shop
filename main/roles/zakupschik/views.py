from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from main.core.view_mixins import LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin
from django.conf import settings
from .fetchers import ZakupschikFetcher
from main.core.constants import Roles


class ZakupschikMainView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    url_name = 'zakupschik'
    allowed_roles = (Roles.ZAKUPSCHIK,)


class ZakupschikOrdersPlacesView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_orders.html'
    url_name = 'zakupschik_orders_places'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['places'] = fetcher.places_to_dict()
        return context


class ZakupschikOrdersByPlacesView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_order_items_by_place.html'
    url_name = 'zakupschik_order_details_by_place'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def __init__(self, *args, **kwargs):
        self.place = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['products'] = fetcher.products_by_place(self.place)
        context['MEDIA_URL'] = settings.MEDIA_URL
        context['place'] = self.place
        return context

    def dispatch(self, request, *args, **kwargs):
        self.place = kwargs.pop('place', None)
        return super().dispatch(request, *args, **kwargs)


class ZakupschikUsersWithProductsToDeliverView(LoginRolesRequiredViewMixin, WithLogedUserInContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_products_ready_to_delivery.html'
    url_name = 'zakupschik_products_ready_to_delivery'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['data'] = fetcher.users_with_ready_to_deliver_products()
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

