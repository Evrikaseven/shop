import os.path
import shutil
from datetime import timedelta
from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import pre_delete, post_save, post_delete
from django.conf import settings
from main.core.models import ModelWithTimestamp, ModelWithUser
from main.core.constants import (
    OrderStatuses,
    Roles,
    OrderItemStatuses,
    OrderItemStates,
    ShoppingTypes,
    DeliveryTypes,
    EXTRA_CHARGE,
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
            raise ValueError(_('The Email must be set'))
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
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    def get_list(self, **kwargs):
        return User.objects.filter(is_staff=False, is_superuser=False, **kwargs)


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = None
    email = models.EmailField('Email адрес', unique=True)
    phone = models.CharField('Телефон', max_length=20)
    location = models.CharField('Адрес', max_length=255)
    birth_date = models.DateField('Дата рождения', blank=True, default='')
    role = models.PositiveSmallIntegerField('Роль', choices=tuple(Roles), default=Roles.UNREGISTERED)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = CustomUserManager()

    class Meta:
        ordering = ('role',)

    def __str__(self):
        return self.email

    @property
    def role_to_string(self):
        return Roles[self.role]


class OrderManager(models.Manager):

    def get_list(self, **kwargs):
        return Order.objects.filter(**kwargs)


class Order(ModelWithTimestamp, ModelWithUser):
    objects = OrderManager()

    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # order_comment = models.TextField(max_length=255, null=True, blank=True)
    # customer_comment = models.TextField(max_length=255, null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=OrderStatuses.CREATED, choices=tuple(OrderStatuses))
    paid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    class Meta:
        ordering = ('created_date',)

    @property
    def price(self):
        order_items_qs = OrderItem.objects.get_used(order=self)
        return (
                sum(oi.price * oi.quantity for oi in order_items_qs.filter(
                    delivery=DeliveryTypes.PURCHASE_AND_DELIVERY
                )) * (1 + EXTRA_CHARGE) +
                sum(oi.price * oi.quantity for oi in order_items_qs.filter(
                    delivery=DeliveryTypes.DELIVERY_ONLY
                )) * EXTRA_CHARGE
        )

    @property
    def actual_price_diff(self):
        return self.actual_price - self.price

    @transaction.atomic
    def update_actual_price_with_user_balance(self):
        if self.actual_price_diff:
            # Update user balance first
            user = self.created_by
            user.balance += self.actual_price_diff
            user.save()
            self.actual_price = self.price
            super().save(update_fields=['actual_price'])

    @property
    def status_to_string(self):
        return OrderStatuses[self.status]

    @transaction.atomic
    def save(self, **kwargs):
        if self.actual_price_diff:
            # Update user balance first
            user = self.created_by
            user.balance += self.actual_price_diff
            user.save()
            self.actual_price = self.price
        super().save(**kwargs)


class OrderItemManager(models.Manager):

    def get_list(self, **kwargs):
        return OrderItem.objects.filter(state__in=(OrderItemStates.ACTIVE, OrderItemStates.USED), **kwargs)

    def get_used(self, **kwargs):
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
                                                default=DeliveryTypes.PURCHASE_AND_DELIVERY,
                                                choices=tuple(DeliveryTypes))

    @property
    def status_to_string(self):
        return OrderItemStatuses[self.status]

    @property
    def delivery_to_string(self):
        return DeliveryTypes[self.delivery]

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


# class SettingOption(models.Model):
#     """
#         Модель настроек с интерфейсом атрибутов
#
#         >>> settings.hello = 'world'
#         Сохранит модель с key='hello' и value='world'. Если модель с таким ключом до этого
#         существовала (т.е. в данный момент мы меняем значение), запись в БД поменяется и кэш
#         инвалидируется.
#
#         >>> settings.hello
#         'world'
#         Получение ключа. Сначала ищет в кэше. Если находит - возвращает, если нет,
#         ищет в БД запись с таким ключом (hello). Если находит - кладёт в кэш и возвращает.
#
#         >>> del settings.hello
#         Удаляет запись с ключом hello из БД и кэша.
#
#         Также, ключ и значение можно редактировать из админки (кэш в этом случает также
#         инвалидируется)
#
#         Пример куска вьюхи, которая может редактировать настройки сайта:
#         if form.is_valid():
#             settings.phone = form.cleaned_data['phone']
#             settings.address = form.cleaned_data['address']
#         """
#
#     s_name = models.CharField(max_length=100, primary_key=True)
#     s_value = models.TextField()
#
#     __cache_ttl = 60 * 60
#     __cache = {}
#     __cache_max_size = 300
#
#     def save(self, *args, **kwargs):
#         super(SettingOption, self).save(*args, **kwargs)
#         # self._cache_invalidate(self.s_name)
#
#     def __getattr__(self, name):
#         value = self._cache_get(name)
#         if value is None:
#             cls = type(self)
#             try:
#                 value = cls.objects.get(pk=name).s_value
#                 self._cache_set(name, value)
#             except cls.DoesNotExist:
#                 value = None
#         return value
#
#     def __setattr__(self, name, value):
#         cls = type(self)
#         try:
#             instance = cls.objects.get(pk=name)
#             instance.__dict__['s_value'] = value
#             instance.save()
#         except cls.DoesNotExist:
#             self.__dict__[name] = value
#             # self.save()
#         # self._cache_set(name, value)
#
#     def __delattr__(self, name):
#         type(self).objects.filter(key=name).delete()
#         self._cache_invalidate(name)
#
#     def _cache_set(self, name, value):
#         if len(self.__cache) < self.__cache_max_size:
#             self._cache_force_set(name, value)
#         else:
#             self._cache_remove_old()
#             if len(self.__cache) < self.__cache_max_size:
#                 self._cache_force_set(name, value)
#
#     def _cache_force_set(self, name, value):
#         self.__cache[name] = (
#             value,
#             timezone.now() + timedelta(seconds=self.__cache_ttl)
#         )
#
#     def _cache_get(self, name):
#         result = self.__cache.get(name)
#         if not result:
#             return None
#         if result[1] > timezone.now():
#             self._cache_invalidate(name)
#             return None
#         return result[0]
#
#     def _cache_invalidate(self, name):
#         del self.__cache[name]
#
#     def _cache_remove_old(self):
#         now = timezone.now()
#         for k, v in self.__cache.items():
#             if v[1] < now:
#                 self._cache_invalidate(k)


def get_path_to_product_image(instance, name):
    return '{}/{}'.format(MEDIA_PROD_IMAGE_DIR_PREFFIX, name)


class ProductManager(models.Manager):

    def get_list(self, **kwargs):
        return Product.objects.filter(**kwargs)

    def get_joint_products(self, **kwargs):
        return Product.objects.filter(shopping_type=ShoppingTypes.JOINT, **kwargs)


class Product(ModelWithTimestamp, ModelWithUser):
    objects = ProductManager()

    name = models.CharField(verbose_name='Название',  max_length=100, default='')
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


def remove_product_image_from_disc(sender, **kwargs):
    instance = kwargs['instance']
    instance.image.delete()
    # directory_to_be_removed = os.path.join(settings.MEDIA_ROOT, "{}{}".format(MEDIA_PROD_IMAGE_DIR_PREFFIX, instance.id))
    # shutil.rmtree(directory_to_be_removed, ignore_errors=True)


@transaction.atomic
def pre_remove_order_item(sender, **kwargs):
    instance = kwargs['instance']
    # TODO: add items handling if CASCADE deleting is not necessary
    if instance.product.shopping_type == ShoppingTypes.INDIVIDUAL:
        instance.product.delete()

    if instance.product.shopping_type == ShoppingTypes.JOINT:
        product = instance.product
        # Update other order items statuses to ACTIVE first
        for oi in product.orderitem_set.all():
            if oi.pk != instance.pk:
                oi.state = OrderItemStates.ACTIVE
                oi.save()
        # Return quantity back to product
        product.quantity += instance.quantity
        product.save()


def post_remove_order_item(sender, **kwargs):
    instance = kwargs['instance']
    order = instance.order
    order.update_actual_price_with_user_balance()


pre_delete.connect(remove_product_image_from_disc, sender=Product)
pre_delete.connect(pre_remove_order_item, sender=OrderItem)
post_delete.connect(post_remove_order_item, sender=OrderItem)

