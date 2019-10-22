import os.path
import shutil
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import pre_delete, post_delete
from django.conf import settings
from django.utils.translation import ugettext as _u
from main.core.models import ModelWithTimestamp, ModelWithUser
from main.core.constants import (
    OrderStatuses,
    Roles,
    OrderItemStatuses,
    OrderItemStates,
    ShoppingTypes,
    PurchaseAndDeliveryTypes,
    DeliveryTypes,
    DELIVERY_PRICES,
)
from main.core.utils import get_file_hash

MEDIA_PROD_IMAGE_DIR_PREFFIX = 'product_images'
MEDIA_ORDER_DIR_PREFFIX = 'order_'
MEDIA_SETTINGS_IMAGES_DIR_PREFFIX = 'settings_images'


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256)
    vk_link = models.CharField(max_length=256)
    place = models.CharField(verbose_name='Место', max_length=150, default='')
    description = models.TextField(blank=True, default='')
    picture = models.CharField(max_length=256)
    product_type = models.CharField(max_length=256, blank=True, default='')


class UserBalance(ModelWithTimestamp):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True)
    delta = models.DecimalField(max_digits=10, decimal_places=2)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_u('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_u('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_u('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    def get_list(self, **kwargs):
        return User.objects.filter(is_staff=False, is_superuser=False, **kwargs)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = None
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20)
    delivery_address = models.CharField('Адрес доставки', max_length=255)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    role = models.PositiveSmallIntegerField('Роль', choices=tuple(Roles), default=Roles.UNREGISTERED)

    objects = CustomUserManager()

    class Meta:
        ordering = ('role',)

    def __str__(self):
        return self.email

    @property
    def role_to_string(self):
        return Roles[self.role]

    @property
    def balance(self):
        return sum(UserBalance.objects.filter(user=self).values_list('delta', flat=True))

    def update_balance_with_delta(self, new_delta):
        if new_delta:
            UserBalance.objects.create(user=self, delta=new_delta)


class OrderManager(models.Manager):

    def get_list(self, **kwargs):
        return Order.objects.filter(**kwargs)


class Order(ModelWithTimestamp, ModelWithUser):
    objects = OrderManager()

    status = models.PositiveSmallIntegerField(default=OrderStatuses.CREATED, choices=tuple(OrderStatuses))
    paid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    delivery = models.PositiveSmallIntegerField(default=DeliveryTypes.PICKUP, choices=tuple(DeliveryTypes))

    class Meta:
        ordering = ('created_date',)

    @property
    def price(self):
        order_items_qs = OrderItem.objects.get_used(order=self)
        extra_charge = SettingOptionHandler('extra_charge').value
        extra_delivery_price = dict(DELIVERY_PRICES)[self.delivery]
        return (
                       sum(oi.price * oi.quantity for oi in order_items_qs.filter(
                           delivery=PurchaseAndDeliveryTypes.PURCHASE_AND_DELIVERY
                       )) * (1 + extra_charge / 100) +
                       sum(oi.price * oi.quantity for oi in order_items_qs.filter(
                           delivery=PurchaseAndDeliveryTypes.DELIVERY_ONLY
                       )) * (extra_charge / 100)
               ) + extra_delivery_price

    @property
    def actual_price_diff(self):
        return self.actual_price - self.price

    @transaction.atomic
    def update_actual_price_with_user_balance(self):
        # The actual price and user balance is updated only for orders in process
        # After it is finished it is frozen for future statistic for example
        if self.actual_price_diff and self.status in (OrderStatuses.CREATED,
                                                      OrderStatuses.PAYING_TO_BE_CONFIRMED,
                                                      OrderStatuses.PAID,
                                                      OrderStatuses.IN_PROGRESS):
            # Update user balance first
            user = self.created_by
            if user:
                user.update_balance_with_delta(self.actual_price_diff)
            self.actual_price = self.price
            super().save(update_fields=['actual_price'])

    @property
    def status_to_string(self):
        return OrderStatuses[self.status]

    @property
    def delivery_to_string(self):
        return DeliveryTypes[self.delivery]

    @property
    def delivery_address(self):
        if self.created_by:
            return self.created_by.delivery_address
        return ''

    @delivery_address.setter
    def delivery_address(self, value):
        if self.created_by:
            self.created_by.delivery_address = value
            self.created_by.save()

    @property
    def all_prices_updated(self):
        if self.orderitem_set.filter(product__price=0).count():
            return False
        return True

    @transaction.atomic
    def save(self, **kwargs):
        if self.actual_price_diff:
            # Update user balance first
            user = self.created_by
            if user:
                user.update_balance_with_delta(self.actual_price_diff)
            self.actual_price = self.price
        super().save(**kwargs)


class OrderItemManager(models.Manager):

    @staticmethod
    def get_list(**kwargs):
        return OrderItem.objects.filter(state__in=(OrderItemStates.ACTIVE, OrderItemStates.USED), **kwargs)

    @staticmethod
    def get_used(**kwargs):
        return OrderItem.objects.filter(state=OrderItemStates.USED, **kwargs)


class OrderItem(ModelWithTimestamp, ModelWithUser):
    objects = OrderItemManager()

    product = models.ForeignKey('Product', verbose_name='Продукт', on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)
    order_comment = models.TextField(verbose_name='Комментарий к заказу', max_length=255, blank=True, default='')
    customer_comment = models.TextField(verbose_name='Комментарий заказчика', max_length=255, blank=True, default='')
    status = models.PositiveSmallIntegerField(verbose_name='Статус',
                                              default=OrderItemStatuses.CREATED,
                                              choices=tuple(OrderItemStatuses))
    state = models.PositiveSmallIntegerField(verbose_name='Состояние',
                                             default=OrderItemStates.USED,
                                             choices=tuple(OrderItemStates))
    parent = models.OneToOneField('self', verbose_name='Заменяемый товар',
                                  on_delete=models.CASCADE, null=True, blank=True)
    delivery = models.PositiveSmallIntegerField(verbose_name='Тип доставки',
                                                default=PurchaseAndDeliveryTypes.PURCHASE_AND_DELIVERY,
                                                choices=tuple(PurchaseAndDeliveryTypes))

    @property
    def status_to_string(self):
        return OrderItemStatuses[self.status]

    @property
    def delivery_to_string(self):
        return PurchaseAndDeliveryTypes[self.delivery]

    @property
    def place(self):
        return self.product.place if self.product else ''

    @property
    def name(self):
        return self.product.name if self.product else ''

    @property
    def price(self):
        return self.product.price if self.product else 0

    @property
    def is_replacement(self):
        return bool(self.parent)


def get_path_to_setting_images(instance, name):
    return '{}/{}'.format(MEDIA_SETTINGS_IMAGES_DIR_PREFFIX, name)


class SettingOptionImages(models.Model):
    image = models.ImageField(upload_to=get_path_to_setting_images)


class SettingOptionManager(models.Manager):

    @staticmethod
    def get_by_name(name):
        try:
            instance = SettingOption.objects.get(s_name=name)
        except ObjectDoesNotExist:
            instance = SettingOption(s_name=name, s_value='')
            instance.save()
        return instance


class SettingOption(models.Model):
    objects = SettingOptionManager()
    s_name = models.CharField(max_length=100, primary_key=True)
    s_value = models.TextField(blank=True, default='')

    @property
    def images(self):
        if self.s_value:
            pks = [int(pk) for pk in self.s_value.split(',')]
            return SettingOptionImages.objects.filter(pk__in=pks)
        return None


class SettingOptionHandler(object):

    def __init__(self, name):
        self.instance = SettingOption.objects.get_by_name(name)

    @property
    def value(self):
        val = self.instance.s_value.strip()
        name = self.instance.s_name
        if name == 'extra_charge':
            val = Decimal(val) if val else Decimal(0)
        elif name == 'work_schedule':
            val = self.instance.images
            if val:
                val = val[0].image
        return val

    @value.setter
    def value(self, value):
        if self.instance.s_name == 'work_schedule':
            if self.instance.s_value:
                obj = self.instance.images[0]
                if obj.image:
                    old_image_hash = get_file_hash(obj.image)
                    new_image_hash = get_file_hash(value)
                    if old_image_hash != new_image_hash:
                        obj.image.delete()
                        obj.image = value
                        obj.save()
                else:
                    obj.image = value
                    obj.save()
            else:
                if value:
                    with transaction.atomic():
                        image = SettingOptionImages(image=value)
                        image.save()
                        self.instance.s_value = str(image.pk)
                        self.instance.save()
        else:
            self.instance.s_value = value
            self.instance.save()


class News(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)
    published = models.DateTimeField(auto_now_add=True, db_index=True)


def get_path_to_product_image(instance, name):
    return '{}/{}'.format(MEDIA_PROD_IMAGE_DIR_PREFFIX, name)


def get_path_to_receipt_image(instance, name):
    order_id = instance.order.id
    return '{}{}/{}'.format(MEDIA_ORDER_DIR_PREFFIX, order_id, name)


class Receipt(ModelWithTimestamp, ModelWithUser):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Фото чека', upload_to=get_path_to_receipt_image)


class ProductManager(models.Manager):

    def get_list(self, **kwargs):
        return Product.objects.filter(**kwargs)

    def get_joint_products(self, **kwargs):
        return Product.objects.filter(shopping_type=ShoppingTypes.JOINT, **kwargs)


class Product(ModelWithTimestamp, ModelWithUser):
    objects = ProductManager()

    name = models.CharField(verbose_name='Название', max_length=100, default='')
    image = models.ImageField(verbose_name='Фото товара', upload_to=get_path_to_product_image)
    place = models.CharField(verbose_name='Место', max_length=150, default='')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2, default=0)
    comment = models.CharField(verbose_name='Комментарий к товару', max_length=255, default='')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    shopping_type = models.PositiveSmallIntegerField(verbose_name='Вид закупки',
                                                     default=ShoppingTypes.INDIVIDUAL,
                                                     choices=tuple(ShoppingTypes))

    @property
    def shopping_type_to_string(self):
        return ShoppingTypes[self.shopping_type]

    def update_order_price(self):
        if self.shopping_type == ShoppingTypes.JOINT:
            if self.quantity == 0:
                self.orderitem_set.all().update(state=OrderItemStates.USED)
                for oi in self.orderitem_set.all():
                    oi.order.update_actual_price_with_user_balance()
            else:  # product.quantity > 0
                self.orderitem_set.all().update(state=OrderItemStates.NOT_ACTIVE)
                for oi in self.orderitem_set.all():
                    oi.order.update_actual_price_with_user_balance()
        else:
            for oi in self.orderitem_set.all():
                oi.order.update_actual_price_with_user_balance()


def remove_product_image_from_disc(sender, **kwargs):
    product = kwargs['instance']
    product.image.delete()
    for order_item in product.orderitem_set.get_list():
        order_item.order.update_actual_price_with_user_balance()


def remove_receipts_images_from_disc(sender, **kwargs):
    order = kwargs['instance']
    directory_to_be_removed = os.path.join(settings.MEDIA_ROOT, "{}{}".format(MEDIA_ORDER_DIR_PREFFIX, order.id))
    shutil.rmtree(directory_to_be_removed, ignore_errors=True)


@transaction.atomic
def post_remove_order_item(sender, **kwargs):
    order_item = kwargs['instance']
    if order_item.product:
        if order_item.product.shopping_type == ShoppingTypes.INDIVIDUAL:
            order_item.product.delete()

        if order_item.product.shopping_type == ShoppingTypes.JOINT:
            product = order_item.product
            # Return quantity back to product
            product.quantity += order_item.quantity
            product.save()
            product.update_order_price()
    order_item.order.update_actual_price_with_user_balance()


post_delete.connect(remove_product_image_from_disc, sender=Product)
pre_delete.connect(remove_receipts_images_from_disc, sender=Order)
post_delete.connect(post_remove_order_item, sender=OrderItem)
