from main.models import Order, OrderStatuses


class ZakupschikFetcher(object):

    def orders_to_dict(self):
        orders_qs = Order.objects.get_list(status=OrderStatuses.CREATED)
        orders = {}
        for order in orders_qs:
            if order.place not in orders:
                orders[order.place] = {}
        return orders

    def places_to_dict(self):
        places = Order.objects.get_list(status=OrderStatuses.CREATED).values_list('place', flat=True)
        return places
