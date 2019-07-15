from main.models import Order, OrderStatuses


class ZakupschikFetcher(object):

    def orders_to_dict(self):
        orders_qs = Order.objects.filter(active=True, status=OrderStatuses.CREATED)
        orders = {}
        for order in orders_qs:
            if order.place not in orders:
                orders[order.place] = {}
        return orders

    def places_to_dict(self):
        places = Order.objects.filter()