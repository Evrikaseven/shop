from main.models import OrderItem
from main.core.constants import OrderStatuses, OrderItemStatuses
from collections import defaultdict


class ZakupschikFetcher(object):

    @staticmethod
    def products_by_place(place):
        order_items_qs = OrderItem.objects.get_list(order__status__in=(OrderStatuses.PAID,
                                                                       OrderStatuses.IN_PROGRESS,
                                                                       OrderStatuses.READY_TO_ISSUE),
                                                    product__place=place,
                                                    status__in=(OrderItemStatuses.CREATED,
                                                                OrderItemStatuses.NOT_BAUGHT_OUT)
                                                    ).select_related('product')
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

    @staticmethod
    def get_orderitems_qs(regex_tmpl: str = r''):
        return OrderItem.objects.get_list(
            order__status__in=(
                OrderStatuses.PAID,
                OrderStatuses.IN_PROGRESS,
                OrderStatuses.READY_TO_ISSUE
            ),
            status__in=(OrderItemStatuses.CREATED, OrderItemStatuses.NOT_BAUGHT_OUT),
            product__place__iregex=regex_tmpl
        )

    @staticmethod
    def get_places_list():
        places = __class__.get_orderitems_qs().values_list('product__place', flat=True)
        return sorted(set(places))

    @staticmethod
    def get_places_tree():
        places = __class__.get_places_list()
        inside_places = defaultdict(dict)
        outside_places = {}
        other_places = []
        for place in places:
            splitted_place = [i for i in place.split('-') if i]
            if len(splitted_place) == 2:
                if splitted_place[0] not in outside_places:
                    outside_places[splitted_place[0]] = [place]
                else:
                    outside_places[splitted_place[0]].append(place)
            elif len(splitted_place) == 3:
                if (splitted_place[0] not in inside_places or
                        splitted_place[1] not in inside_places[splitted_place[0]]):
                    inside_places[splitted_place[0]][splitted_place[1]] = [place]
                else:
                    inside_places[splitted_place[0]][splitted_place[1]].append(place)
            else:
                other_places.append(place)
        return {
            'inside_places': inside_places,
            'outside_places': outside_places,
            'other_places': other_places
        }

    @staticmethod
    def users_with_ready_to_deliver_products():
        order_items_qs = OrderItem.objects.filter(order__status__in=(OrderStatuses.PAID,
                                                                     OrderStatuses.IN_PROGRESS,
                                                                     OrderStatuses.READY_TO_ISSUE),
                                                  status=OrderItemStatuses.BAUGHT_OUT
                                                  ).select_related('order__created_by', 'product')
        ready_product_by_users_dict = defaultdict(dict)
        for item in order_items_qs:
            user = item.order.created_by
            if user.pk not in ready_product_by_users_dict:
                ready_product_by_users_dict[user.pk]['items'] = [item]
                ready_product_by_users_dict[user.pk]['user'] = user
            else:
                ready_product_by_users_dict[user.pk]['items'].append(item)
        return ready_product_by_users_dict.values()
