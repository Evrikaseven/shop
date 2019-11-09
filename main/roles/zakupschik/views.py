from django.views.generic.base import TemplateView
from main.core.view_mixins import LoginRolesRequiredViewMixin, CommonContextViewMixin
from django.conf import settings
from .fetchers import ZakupschikFetcher
from main.core.constants import Roles, OrderItemStatuses


class ZakupschikMainView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)


class ZakupschikLocationsView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_locations.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)


class ZakupschikLocationsFloorsView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_locations_floors.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def __init__(self, *args, **kwargs):
        self.location = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        floors = {}
        if self.location == 'building1':
            floors = fetcher.get_places_tree()['building1_places']
        if self.location == 'tdb':
            floors = fetcher.get_places_tree()['tdb_places']
        context['location'] = self.location
        context['floors'] = floors.keys()
        return context

    def dispatch(self, request, *args, **kwargs):
        self.location = kwargs['location']
        return super().dispatch(request, *args, **kwargs)


class ZakupschikLocationsLinesView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_locations_lines.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def __init__(self, *args, **kwargs):
        self.location = None
        self.floor = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        if self.location == 'outside':
            lines = fetcher.get_places_tree()['outside_places']
        elif self.location == 'building1':
            lines = fetcher.get_places_tree()['building1_places'][self.floor]
        elif self.location == 'tdb':
            lines = fetcher.get_places_tree()['tdb_places'][self.floor]
        context['location'] = self.location
        context['floor'] = self.floor
        context['lines'] = lines.keys()
        return context

    def dispatch(self, request, *args, **kwargs):
        self.location = kwargs['location']
        self.floor = kwargs['floor']
        return super().dispatch(request, *args, **kwargs)


class ZakupschikPlacesView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
    template_name = 'main/zakupschik_places.html'
    allowed_roles = (Roles.ZAKUPSCHIK,)

    def __init__(self, *args, **kwargs):
        self.location = None
        self.floor = None
        self.line = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        if self.location == 'other':
            context['places'] = fetcher.get_places_tree()['other_places']
        elif self.location == 'building1':
            context['places'] = fetcher.get_places_tree()['building1_places'][self.floor][self.line]
        elif self.location == 'outside':
            context['places'] = fetcher.get_places_tree()['outside_places'][self.line]
        elif self.location == 'tdb':
            context['places'] = fetcher.get_places_tree()['tdb_places'][self.floor][self.line]
        else:
            context['places'] = fetcher.get_places_list()
        return context

    def dispatch(self, request, *args, **kwargs):
        self.location = kwargs['location']
        self.floor = kwargs['floor']
        self.line = kwargs['line']
        return super().dispatch(request, *args, **kwargs)


class ZakupschikOrderItemsByPlaceView(LoginRolesRequiredViewMixin, CommonContextViewMixin, TemplateView):
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
