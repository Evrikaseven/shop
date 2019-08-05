from main.models import Order, OrderItem
from main.core.constants import OrderStatuses


class ZakupschikFetcher(object):

    def order_items_by_place(self, place):
        order_items_qs = OrderItem.objects.get_list(order__status__in=(OrderStatuses.PAYING_TO_BE_CONFIRMED,
                                                                       OrderStatuses.PAID,
                                                                       OrderStatuses.IN_PROGRESS,
                                                                       OrderStatuses.READY_TO_ISSUE),
                                                    place=place)
        return order_items_qs

    def places_to_dict(self):
        places = OrderItem.objects.get_list(order__status__in=(
                                                        OrderStatuses.PAYING_TO_BE_CONFIRMED,
                                                        OrderStatuses.PAID,
                                                        OrderStatuses.IN_PROGRESS,
                                                        OrderStatuses.READY_TO_ISSUE
                                                    )).values_list('place', flat=True)
        return set(places)
