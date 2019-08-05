from main.models import Order, OrderItem
from main.core.constants import OrderStatuses


class ZakupschikFetcher(object):

    def orders_by_place(self, place):
        orders_qs = Order.objects.get_list(status__in=(OrderStatuses.PAYING_TO_BE_CONFIRMED,
                                                       OrderStatuses.PAID,
                                                       OrderStatuses.IN_PROGRESS,
                                                       OrderStatuses.READY_TO_ISSUE))
        return orders_qs

    def places_to_dict(self):
        places = OrderItem.objects.get_list(order__status__in=(
                                                        OrderStatuses.PAYING_TO_BE_CONFIRMED,
                                                        OrderStatuses.PAID,
                                                        OrderStatuses.IN_PROGRESS,
                                                        OrderStatuses.READY_TO_ISSUE
                                                    )).values_list('place', flat=True)
        return set(places)
