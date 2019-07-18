from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .fetchers import ZakupschikFetcher


class ZakupschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik.html'
    url_name = 'zakupschik'


class ZakupschikIndividualOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik_individual_orders.html'
    url_name = 'zakupschik_individual_orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['places'] = fetcher.places_to_dict()
        return context


class ZakupschikOrdersByPlacesView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik_order_details_by_place.html'
    url_name = 'zakupschik_order_details_by_place'

    def __init__(self):
        self.place = None

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fetcher = ZakupschikFetcher()
        context['orders'] = fetcher.orders_by_place(self.place)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.place = kwargs.pop('place', None)
        return super().dispatch(request, *args, **kwargs)


class ZakupschikJointOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'main/zakupschik_joint_orders.html'
    url_name = 'zakupschik_joint_orders'


