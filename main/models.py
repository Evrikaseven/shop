from enum import EnumMeta
from django.db import models
from django.contrib.auth.models import AbstractUser
from main.core.models import ModelWithTimestamp, ModelWithUser


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    vk_link = models.CharField(max_length=256, null=True, blank=True)
    place = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=256, null=True, blank=True)
    product_type = models.CharField(max_length=256, null=True, blank=True)


class Roles(EnumMeta):
    ZAKAZSCHIK = 0
    SBORSCHIK = 1
    ZAKUPSCHIK = 2
    ADMINISTRATOR = 3


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    ZAKAZSCHIK = 'Заказчик'
    SBORSCHIK = 'Сборщик'
    ZAKUPSCHIK = 'Закупщик'
    ADMINISTRATOR = 'Администратор'
    ROLES = (
        (Roles.ZAKAZSCHIK, ZAKAZSCHIK),
        (Roles.SBORSCHIK, SBORSCHIK),
        (Roles.ZAKUPSCHIK, ZAKUPSCHIK),
        (Roles.ADMINISTRATOR, ADMINISTRATOR),
    )
    role = models.PositiveIntegerField(choices=ROLES, default=Roles.ZAKAZSCHIK)


def get_path_to_order_images(instance, name):
    return 'order_{}'.format(instance.id)


class OrderStatuses(EnumMeta):
    CREATED = 0
    PAID = 1
    CLOSED = 2


class OrderManager(models.Manager):

    def get_list(self):
        return Order.objects.filter(active=True)


class Order(ModelWithTimestamp, ModelWithUser):
    objects = OrderManager()
    # image = models.ImageField(upload_to=get_path_to_order_images)
    place = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    order_comment = models.TextField(max_length=255, null=True, blank=True)
    customer_comment = models.TextField(max_length=255, null=True, blank=True)

    ORDER_STATUSES = (
        (OrderStatuses.CREATED, 'Создан'),
        (OrderStatuses.PAID, 'Оплачен'),
        (OrderStatuses.CLOSED, 'Закрыт'),
    )
    status = models.PositiveIntegerField(default=OrderStatuses.CREATED, choices=ORDER_STATUSES)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created_date', )


class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to=get_path_to_order_images)
    comment = models.CharField(max_length=255, null=True, blank=True)
    selected = models.BooleanField(default=True)

