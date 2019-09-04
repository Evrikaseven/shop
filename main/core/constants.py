from .types import EnumMetaWithStrings
from decimal import Decimal


class Roles(metaclass=EnumMetaWithStrings):
    UNREGISTERED = 0, 'Незарегистрирован'
    ZAKAZSCHIK = 1, 'Заказчик'
    ZAKUPSCHIK = 2, 'Закупщик'
    ADMINISTRATOR = 3, 'Администратор'


class OrderStatuses(metaclass=EnumMetaWithStrings):
    CREATED = 0, 'Неоплачен'
    PAYING_TO_BE_CONFIRMED = 1, 'Оплата в процессе подтверждения'
    PAID = 2, 'Оплата подтверждена'
    IN_PROGRESS = 3, 'В обработке'
    READY_TO_ISSUE = 4, 'Готов к выдаче'
    CLOSED = 5, 'Закрыт'


class OrderItemStatuses(metaclass=EnumMetaWithStrings):
    CREATED = 0, 'Создан'
    BAUGHT_OUT = 1, 'Выкуплен'
    NOT_BAUGHT_OUT = 2, 'Не выкуплен'


class OrderItemStates(metaclass=EnumMetaWithStrings):
    NOT_ACTIVE = 0, 'Не активный'
    ACTIVE = 1, 'Активный'
    USED = 2, 'Используется'


class ShoppingTypes(metaclass=EnumMetaWithStrings):
    INDIVIDUAL = 0, 'Индивидуальная покупка'
    JOINT = 1, ' Совместная покупка'


class PurchaseAndDeliveryTypes(metaclass=EnumMetaWithStrings):
    PURCHASE_AND_DELIVERY = 0, 'Закупка вместе с доставкой'
    DELIVERY_ONLY = 1, 'Только доставка'


class DeliveryTypes(metaclass=EnumMetaWithStrings):
    PICKUP = 0, 'Самовывоз'
    STORAGE = 1, 'Хранение'
    POST_MAIL = 2, 'Почта'
    HOME_DELIVEY = 3, 'Доставка на дом'
    TK = 4, 'Транспортная компания'


DELIVERY_PRICES = (
    (DeliveryTypes.PICKUP, 0),
    (DeliveryTypes.STORAGE, 0),
    (DeliveryTypes.POST_MAIL, 100),
    (DeliveryTypes.HOME_DELIVEY, 150),
    (DeliveryTypes.TK, 150),
)


SHOP_TITLE = chr(214) + 'П*ТЫ'


