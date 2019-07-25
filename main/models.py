import os.path
import shutil
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.conf import settings
from main.core.models import ModelWithTimestamp, ModelWithUser
from main.core.constants import OrderStatuses, Roles


MEDIA_DIR_PREFFIX = 'order_'


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    vk_link = models.CharField(max_length=256, null=True, blank=True)
    place = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=256, null=True, blank=True)
    product_type = models.CharField(max_length=256, null=True, blank=True)


class User(AbstractUser):
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True, )
    location = models.CharField('Адрес', max_length=255, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)

    ROLES = (
        (Roles.UNREGISTERED, Roles.UNREGISTERED_STR),
        (Roles.ZAKAZSCHIK, Roles.ZAKAZSCHIK_STR),
        (Roles.ZAKUPSCHIK, Roles.ZAKUPSCHIK_STR),
        (Roles.ADMINISTRATOR, Roles.ADMINISTRATOR_STR),
    )
    role = models.PositiveIntegerField('Роль', choices=ROLES, default=Roles.UNREGISTERED)

    @property
    def role_to_string(self):
        roles = dict(self.ROLES)
        return roles[self.role]


def get_path_to_order_images(instance, name):
    return '{}{}/{}'.format(MEDIA_DIR_PREFFIX, instance.order.pk, name)


class OrderManager(models.Manager):

    def get_list(self, **kwargs):
        return Order.objects.filter(active=True, **kwargs)


class Order(ModelWithTimestamp, ModelWithUser):
    objects = OrderManager()
    place = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    order_comment = models.TextField(max_length=255, null=True, blank=True)
    customer_comment = models.TextField(max_length=255, null=True, blank=True)

    ORDER_STATUSES = (
        (OrderStatuses.CREATED, OrderStatuses.CREATED_STR),
        (OrderStatuses.PAID, OrderStatuses.PAID_STR),
        (OrderStatuses.IN_PROGRESS, OrderStatuses.IN_PROGRESS_STR),
        (OrderStatuses.READY_TO_ISSUE, OrderStatuses.READY_TO_ISSUE_STR),
        (OrderStatuses.CLOSED, OrderStatuses.CLOSED_STR),
    )
    status = models.PositiveIntegerField(default=OrderStatuses.CREATED, choices=ORDER_STATUSES)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created_date', )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def status_to_string(self):
        statuses = dict(self.ORDER_STATUSES)
        return statuses[self.status]


def remove_order_images_from_disc(sender, **kwargs):
    instance = kwargs['instance']
    directory_to_be_removed = os.path.join(settings.MEDIA_ROOT, "{}{}".format(MEDIA_DIR_PREFFIX, instance.id))
    shutil.rmtree(directory_to_be_removed, ignore_errors=True)


class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=get_path_to_order_images)
    comment = models.CharField(max_length=255, null=True, blank=True)
    selected = models.BooleanField(default=True)


pre_delete.connect(remove_order_images_from_disc, sender=Order)
