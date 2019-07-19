from enum import EnumMeta

class Roles(EnumMeta):
    ZAKAZSCHIK = 0
    SBORSCHIK = 1
    ZAKUPSCHIK = 2
    ADMINISTRATOR = 3


class OrderStatuses(EnumMeta):
    CREATED = 0
    PAID = 1
    CLOSED = 2


