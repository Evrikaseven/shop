from .types import EnumMetaWithStrings


class Roles(metaclass=EnumMetaWithStrings):
    UNREGISTERED = 0, 'Незарегистрирован'
    ZAKAZSCHIK = 1, 'Заказчик'
    ZAKUPSCHIK = 2, 'Закупщик'
    ADMINISTRATOR = 3, 'Администратор'


class OrderStatuses(metaclass=EnumMetaWithStrings):
    CREATED = 0, 'Создан'
    PAID = 1, 'Оплачен'
    CLOSED = 2, 'Закрыт'


