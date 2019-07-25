from main.models import Order
from main.core.constants import OrderStatuses


class ZakazschikFetcher(object):

    def orders_by_id(self, id):
        orders_qs = Order.objects.get_list(status=OrderStatuses.CREATED, id=id)
        return orders_qs
