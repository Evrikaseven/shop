from django.db import models
from django.contrib.auth.models import User, AbstractUser


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    vk_link = models.CharField(max_length=256, null=True, blank=True)
    space = models.CharField(max_length=150, null=True, blank=True)
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
