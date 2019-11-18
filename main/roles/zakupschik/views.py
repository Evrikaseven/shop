from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from main.core.view_mixins import LoginRolesRequiredViewMixin, CommonContextViewMixin
from django.conf import settings
from django.shortcuts import redirect
from .fetchers import ZakupschikFetcher
from .forms import ZakupschikProductForm, ZakupschikProductBaseFormSet
from django.forms import modelformset_factory
from main.core.constants import Roles, OrderItemStatuses
from main.models import Product


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
    ZakupschikProductFormSet = modelformset_factory(Product, ZakupschikProductForm,
                                                    formset=ZakupschikProductBaseFormSet, extra=0)

    def __init__(self, *args, **kwargs):
        self.place = None
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:zakupschik_order_details_by_place', kwargs={'place': self.place})

    def get_context_data(self, **kwargs):
        products = ZakupschikFetcher.products_by_place(self.place)
        formset = self.ZakupschikProductFormSet(queryset=Product.objects.get_list(pk__in=products.keys()))
        context = super().get_context_data(**kwargs)
        context['formset'] = formset
        context['products_list'] = products.values()
        context['order_items_statuses_list'] = list(OrderItemStatuses)
        context['total_sum'] = sum(p['total_quantity'] * p['price'] for p in products.values())
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def post(self, *args, **kwargs):
        products = ZakupschikFetcher.products_by_place(self.place)
        formset = self.ZakupschikProductFormSet(self.request.POST, queryset=Product.objects.get_list(pk__in=products.keys()))
        if formset.is_valid():
            pass
        return redirect(self.get_success_url())

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
