from main.models import Order, OrderItem
from main.core.constants import OrderStatuses, OrderItemStatuses
from collections import defaultdict


class ZakupschikFetcher(object):

    def products_by_place(self, place):
        order_items_qs = OrderItem.objects.get_list(order__status__in=(OrderStatuses.PAID,
                                                                       OrderStatuses.IN_PROGRESS,
                                                                       OrderStatuses.READY_TO_ISSUE),
                                                    product__place=place)
        products_dict = defaultdict(dict)
        for item in order_items_qs:
            if item.product.pk not in products_dict:
                products_dict[item.product.pk]['items'] = [item]
                products_dict[item.product.pk]['item_status_str'] = item.status_to_string
                # first added, other statuses and prices should be the same
                products_dict[item.product.pk]['total_quantity'] = item.quantity
                products_dict[item.product.pk]['price'] = item.price
                products_dict[item.product.pk]['product'] = item.product
            else:
                products_dict[item.product.pk]['items'].append(item)
                products_dict[item.product.pk]['total_quantity'] += item.quantity
        return products_dict.values()

    def places_to_dict(self):
        places = OrderItem.objects.get_list(
            order__status__in=(
                OrderStatuses.PAID,
                OrderStatuses.IN_PROGRESS,
                OrderStatuses.READY_TO_ISSUE
            ),
            status__in=(OrderItemStatuses.CREATED, OrderItemStatuses.NOT_BAUGHT_OUT)
        ).values_list('product__place', flat=True)
        return sorted(set(places))
