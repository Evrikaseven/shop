from main.models import Order
from main.core.constants import OrderStatuses


class ZakupschikFetcher(object):

    def orders_by_place(self, place):
        orders_qs = Order.objects.get_list(status=OrderStatuses.CREATED, place=place)
        return orders_qs

    def places_to_dict(self):
        places = Order.objects.get_list(status=OrderStatuses.CREATED).values_list('place', flat=True)
        return set(places)
