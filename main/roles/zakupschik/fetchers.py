from main.models import OrderItem
from main.core.constants import OrderStatuses, OrderItemStatuses
from collections import defaultdict
import re


class ZakupschikFetcher(object):

    LOCATIONS = {
        'building1': 0,
        'tbd': 1,
        'outside': 2,
        'other': 3
    }

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
                products_dict[item.product.pk]['total_quantity'] = item.quantity
                products_dict[item.product.pk]['price'] = item.price
            else:
                products_dict[item.product.pk]['total_quantity'] += item.quantity
        return products_dict

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

    @classmethod
    def get_places_list(cls):
        places = cls.get_orderitems_qs().values_list('product__place', flat=True)
        return sorted(set(places))

    @classmethod
    def _get_splitted_place(cls, place):
        splitted_place = [i for i in place.split('-') if i]
        if len(splitted_place) == 2:
            # check for 2d-123 | 1g-444 examples
            m = re.search(r'^([1,2])(\w+)', splitted_place[0])
            if m and m.group(2).isalpha():
                splitted_place = m.group(1), m.group(2), splitted_place[1]
                return cls.LOCATIONS['building1'], splitted_place
            # check for tdb examples
            m = re.search(r'^(tdb|тдб)(\w+)', splitted_place[0])
            if m and m.group(2).isnumeric():
                splitted_place = m.group(1), m.group(2), splitted_place[1]
                return cls.LOCATIONS['tbd'], splitted_place
            return cls.LOCATIONS['outside'], splitted_place
        elif len(splitted_place) == 3:
            return cls.LOCATIONS['building1'], splitted_place
        return cls.LOCATIONS['other'], splitted_place

    @classmethod
    def get_places_tree(cls):
        places = cls.get_places_list()
        building1_places = defaultdict(dict)
        tdb_places = defaultdict(dict)
        outside_places = {}
        other_places = []
        for place in places:
            location, splitted_place = cls._get_splitted_place(place)

            if location == cls.LOCATIONS['building1']:
                if (splitted_place[0] not in building1_places or
                        splitted_place[1] not in building1_places[splitted_place[0]]):
                    building1_places[splitted_place[0]][splitted_place[1]] = [place]
                else:
                    building1_places[splitted_place[0]][splitted_place[1]].append(place)

            elif location == cls.LOCATIONS['tbd']:
                if (splitted_place[0] not in tdb_places or
                        splitted_place[1] not in tdb_places[splitted_place[0]]):
                    tdb_places[splitted_place[1]][splitted_place[2]] = [place]
                else:
                    tdb_places[splitted_place[1]][splitted_place[2]].append(place)

            elif location == cls.LOCATIONS['outside']:
                if splitted_place[0] not in outside_places:
                    outside_places[splitted_place[0]] = [place]
                else:
                    outside_places[splitted_place[0]].append(place)

            else:
                other_places.append(place)
        return {
            'building1_places': building1_places,
            'outside_places': outside_places,
            'other_places': other_places,
            'tdb_places': tdb_places,
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
