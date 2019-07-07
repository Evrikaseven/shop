from django.db import models
from django.contrib.auth.models import AbstractUser
from main.core.mixins import WithTimestampMixin, WithUserMixin


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    vk_link = models.CharField(max_length=256, null=True, blank=True)
    place = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=256, null=True, blank=True)
    product_type = models.CharField(max_length=256, null=True, blank=True)


class Roles(object):
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


class Order(WithTimestampMixin, WithUserMixin, models.Model):
    image = models.ImageField(blank=True, null=True)
    place = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    order_comment = models.TextField(max_length=255, null=True, blank=True)
    customer_comment = models.TextField(max_length=255, null=True, blank=True)

