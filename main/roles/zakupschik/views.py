from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, CommonContextViewMixin
from django.conf import settings
from .fetchers import ZakupschikFetcher
from main.core.constants import Roles, OrderItemStatuses


class ZakupschikMainView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)


class ZakupschikOrdersPlacesView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_orders.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['places'] = fetcher.places_to_dict()
        return context


class ZakupschikOrdersByPlacesView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_order_items_by_place.html'
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
        context['order_items_statuses_list'] = list(OrderItemStatuses)[1:]
        return context

    def dispatch(self, request, *args, **kwargs):
        self.place = kwargs.pop('place', None)
        return super().dispatch(request, *args, **kwargs)


class ZakupschikUsersWithProductsToDeliverView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_products_ready_to_delivery.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['data'] = fetcher.users_with_ready_to_deliver_products()
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context
