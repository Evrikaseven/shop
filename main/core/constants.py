from .types import EnumMetaWithStrings


class Roles(metaclass=EnumMetaWithStrings):
    UNREGISTERED = 0, 'Незарегистрирован'
    ZAKAZSCHIK = 1, 'Заказчик'
    ZAKUPSCHIK = 2, 'Закупщик'
    ADMINISTRATOR = 3, 'Администратор'


class OrderStatuses(metaclass=EnumMetaWithStrings):
    CREATED = 0, 'Неоплачен'
    PAID = 1, 'Оплачен'
    IN_PROGRESS = 2, 'В обработке'
    READY_TO_ISSUE = 3, 'Готов к выдаче'
    CLOSED = 4, 'Закрыт'

