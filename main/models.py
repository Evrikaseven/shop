import os.path
import shutil
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.conf import settings
from main.core.models import ModelWithTimestamp, ModelWithUser
from main.core.constants import (
    OrderStatuses,
    Roles,
    OrderItemStatuses,
    ShoppingTypes
)


MEDIA_PROD_IMAGE_DIR_PREFFIX = 'product_images'


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256)
    vk_link = models.CharField(max_length=256)
    place = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    picture = models.CharField(max_length=256)
    product_type = models.CharField(max_length=256, blank=True, default='')


class User(AbstractUser):
    phone = models.CharField('Телефон', max_length=20)
    location = models.CharField('Адрес', max_length=255)
    birth_date = models.DateField('Дата рождения', blank=True, default='')

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


class OrderManager(models.Manager):

    def get_list(self, **kwargs):
        return Order.objects.filter(active=True, **kwargs)


class Order(ModelWithTimestamp, ModelWithUser):
    objects = OrderManager()

    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # order_comment = models.TextField(max_length=255, null=True, blank=True)
    # customer_comment = models.TextField(max_length=255, null=True, blank=True)

    ORDER_STATUSES = (
        (OrderStatuses.CREATED, OrderStatuses.CREATED_STR),
        (OrderStatuses.PAYING_TO_BE_CONFIRMED, OrderStatuses.PAYING_TO_BE_CONFIRMED_STR),
        (OrderStatuses.PAID, OrderStatuses.PAID_STR),
        (OrderStatuses.IN_PROGRESS, OrderStatuses.IN_PROGRESS_STR),
        (OrderStatuses.READY_TO_ISSUE, OrderStatuses.READY_TO_ISSUE_STR),
        (OrderStatuses.CLOSED, OrderStatuses.CLOSED_STR),
    )
    status = models.PositiveIntegerField(default=OrderStatuses.CREATED, choices=ORDER_STATUSES)
    active = models.BooleanField(default=True)
    paid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def price(self):
        return sum(oi.price * oi.quantity for oi in OrderItem.objects.get_list(order=self))

    @property
    def balance(self):
        return self.price - self.paid_price

    class Meta:
        ordering = ('created_date', )

    @property
    def status_to_string(self):
        statuses = dict(self.ORDER_STATUSES)
        return statuses[self.status]


class OrderItemManager(models.Manager):

    def get_list(self, **kwargs):
        return OrderItem.objects.filter(active=True, **kwargs)


class OrderItem(ModelWithTimestamp, ModelWithUser):
    objects = OrderItemManager()

    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    order_comment = models.TextField(max_length=255, blank=True, default='')
    customer_comment = models.TextField(max_length=255, blank=True, default='')
    ORDER_ITEM_STATUSES = (
        (OrderItemStatuses.CREATED, OrderItemStatuses.CREATED_STR),
        (OrderItemStatuses.BAUGHT_OUT, OrderItemStatuses.BAUGHT_OUT_STR),
        (OrderItemStatuses.NOT_BAUGHT_OUT, OrderItemStatuses.NOT_BAUGHT_OUT_STR),
    )
    status = models.PositiveIntegerField(default=OrderItemStatuses.CREATED, choices=ORDER_ITEM_STATUSES)
    active = models.BooleanField(default=True)

    @property
    def status_to_string(self):
        statuses = dict(self.ORDER_ITEM_STATUSES)
        return statuses[self.status]

    @property
    def place(self):
        return self.product.place if self.product else None

    @place.setter
    def place(self, value):
        self.product.place = value
        self.product.save()


def get_path_to_product_image(instance, name):
    return '{}/{}'.format(MEDIA_PROD_IMAGE_DIR_PREFFIX, name)


class ProductManager(models.Manager):

    def get_list(self, **kwargs):
        return Product.objects.filter(active=True, **kwargs)

    def get_joint_products(self, **kwargs):
        return Product.objects.filter(active=True, shopping_type=ShoppingTypes.JOINT, **kwargs)


class Product(ModelWithTimestamp, ModelWithUser):
    objects = ProductManager()

    image = models.ImageField(verbose_name='Фото товара', upload_to=get_path_to_product_image)
    place = models.CharField(verbose_name='Место', max_length=150, default='')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2, default=0)
    comment = models.CharField(verbose_name='Комментарий к товару', max_length=255, default='')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    active = models.BooleanField(default=True)
    SHOPPING_TYPES = (
        (ShoppingTypes.INDIVIDUAL, ShoppingTypes.INDIVIDUAL_STR),
        (ShoppingTypes.JOINT, ShoppingTypes.JOINT_STR),
    )
    shopping_type = models.PositiveIntegerField(verbose_name='Вид закупки', default=ShoppingTypes.INDIVIDUAL, choices=SHOPPING_TYPES)

    @property
    def shopping_type_to_string(self):
        types = dict(self.SHOPPING_TYPES)
        return types[self.shopping_type]


def remove_product_image_from_disc(sender, **kwargs):
    instance = kwargs['instance']
    instance.image.delete()
    # directory_to_be_removed = os.path.join(settings.MEDIA_ROOT, "{}{}".format(MEDIA_PROD_IMAGE_DIR_PREFFIX, instance.id))
    # shutil.rmtree(directory_to_be_removed, ignore_errors=True)


def remove_order_item(sender, **kwargs):
    instance = kwargs['instance']
    if instance.product.shopping_type == ShoppingTypes.INDIVIDUAL:
        instance.product.delete()


pre_delete.connect(remove_product_image_from_disc, sender=Product)
pre_delete.connect(remove_order_item, sender=OrderItem)


