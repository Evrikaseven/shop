from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from main.emails import user_data_email, order_data_email
from django.db import transaction
from .models import (
    Provider,
    Order,
    OrderItem,
    Product,
    User,
    SettingOptionHandler,
    Receipt,
    News,
)
from main.core import widgets as custom_widgets, form_fields as custom_form_fields
from main.core.constants import (
    Roles,
    OrderStatuses,
    ShoppingTypes,
    OrderItemStates,
    OrderItemStatuses,
    DeliveryTypes,
)
from main.core.form_mixins import WithUserDataUpdateFormMixin


class ProviderForm(forms.ModelForm):
    name = forms.CharField(label='Имя', help_text='Имя поставщика')
    vk_link = forms.CharField(label='Ссылка Вконтакте', help_text='URL профиля Вконтакте')
    place = forms.CharField(label='Место', help_text='Номер места поставщика')
    description = forms.CharField(label='Описание', widget=forms.Textarea, help_text='Описание с данными поставщика')
    picture = forms.CharField(label='Изображение', help_text='URL либо путь к картинке')
    product_type = forms.CharField(label='Чем торгует', help_text='Вид товара')

    class Meta:
        model = Provider
        fields = ['name', 'vk_link', 'place', 'description', 'picture', 'product_type']


class NewOrderForm(WithUserDataUpdateFormMixin, forms.ModelForm):
    images = custom_form_fields.MultipleFilesField(label='Изображение товара',
                                                   widget=custom_widgets.ClearableMultiFileInput())
    status = forms.ChoiceField(required=False, choices=tuple(OrderStatuses))

    class Meta:
        model = Order
        fields = ('images', 'status')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if getattr(self.user, 'role', Roles.UNREGISTERED) not in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            self.fields.pop('status')

    def clean_images(self):
        images = self.cleaned_data['images']
        if not images:
            raise ValidationError('Добавьте фотографию хотя бы одного товара')
        return images

    @transaction.atomic
    def save(self, commit=True):
        super().save(commit=commit)

        order_items = []
        for image in self.cleaned_data['images']:
            product = Product(image=image, created_by=self.user, updated_by=self.user)
            product.save()
            # order_item = OrderItem(order=self.instance, product=product, created_by=self.user, updated_by=self.user)
            # order_item.save()
            # to optimize with bulk create
            order_items.append(
                OrderItem(order=self.instance, product=product, created_by=self.user, updated_by=self.user))
        if order_items:
            OrderItem.objects.bulk_create(order_items)
        return self.instance


class OrderForm(WithUserDataUpdateFormMixin, forms.ModelForm):
    images = custom_form_fields.MultipleFilesField(label='Изображение товара',
                                                   widget=custom_widgets.ClearableMultiFileInput())
    status = forms.ChoiceField(required=False, choices=tuple(OrderStatuses))
    delivery = forms.ChoiceField(required=False, choices=tuple(DeliveryTypes))
    delivery_address = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('images', 'status', 'paid_price', 'delivery', 'delivery_address')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_balance_delta = 0
        self.status_changed = False
        super().__init__(*args, **kwargs)

        role = getattr(self.user, 'role', Roles.UNREGISTERED)
        if role not in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            self.fields.pop('status')
        if role == Roles.UNREGISTERED:
            self.fields.pop('delivery')
            self.fields.pop('delivery_address')

    @transaction.atomic
    def pay_order(self):
        self.instance.status = OrderStatuses.PAYING_TO_BE_CONFIRMED
        user = self.instance.created_by
        if user:
            old_user_balance = user.balance
            self.instance.save()

            if old_user_balance != user.balance:
                user_data_email(user=user,
                                subject='Баланс пользователя изменен',
                                extra_params={'balance_changed': True})

            order_data_email(order=self.instance,
                             subject='Новый заказ №{}'.format(self.instance.pk),
                             extra_params={'status_changed': True})

    def clean_paid_price(self):
        paid_price = self.cleaned_data['paid_price']
        return paid_price if paid_price else 0

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk:
            paid_price = cleaned_data['paid_price']
            cleaned_data['paid_price'] = self.instance.paid_price + paid_price
            self.user_balance_delta = paid_price
            if 'status' in self.cleaned_data and self.instance.status != cleaned_data['status']:
                self.status_changed = True
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = self.instance.created_by
        if user:
            if self.status_changed:
                order_data_email(order=self.instance,
                                 subject='Статус заказа №{} изменен'.format(self.instance.pk),
                                 extra_params={'status_changed': True})
            if self.user_balance_delta:
                user.balance += self.user_balance_delta
                user.save()
                user_data_email(user=user,
                                subject='Баланс пользователя изменен',
                                extra_params={'balance_changed': True})
            if ('delivery_address' in self.cleaned_data and self.cleaned_data['delivery_address'] and
                    self.cleaned_data['delivery_address'] != self.instance.delivery_address):
                self.instance.delivery_address = self.cleaned_data['delivery_address']

        return super().save(commit=True)


class ReceiptForOrderForm(forms.ModelForm):

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        super().__init__(**kwargs)

        if self.is_image_update_forbidden:
            self.fields.pop('product_image')

    class Meta:
        model = Receipt
        fields = ('image',)

    # def clean_check_image(self):
    #     image = self.cleaned_data['check_image']
    #     if not image and not self.instance.pk:
    #         raise ValidationError('Добавьте фотографию чека')
    #     return image

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
        return super().save(commit=commit)


class OrderItemForm(WithUserDataUpdateFormMixin, forms.ModelForm):
    image = forms.ImageField(label='Изображение товара', required=False)
    place = forms.CharField(label='Место')
    name = forms.CharField(label='Название товара', required=False)
    price = forms.DecimalField(label='Цена товара', required=False)

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        self.parent_item = kwargs.pop('parent_item', None)
        self.joint_quantity_delta = 0
        super().__init__(**kwargs)

        self.fields['name'].initial = self.instance.name
        self.fields['place'].initial = self.instance.place
        self.fields['price'].initial = self.instance.price
        if self.is_image_update_forbidden:
            self.fields.pop('image')
        if self.user:
            if self.user.role == Roles.ZAKAZSCHIK:
                self.fields['status'].disabled = True
            if self.user.role == Roles.ZAKUPSCHIK:
                self.fields['delivery'].disabled = True
            if (self.user.role in (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK) and self.instance.pk and
                    self.instance.product.shopping_type == ShoppingTypes.JOINT):
                self.fields['delivery'].disabled = True
                self.fields['place'].disabled = True
                self.fields['name'].disabled = True
                self.fields['price'].disabled = True

    class Meta:
        model = OrderItem
        fields = ('image',
                  'name',
                  'place',
                  'price',
                  'quantity',
                  'status',
                  'delivery',
                  'order_comment',
                  'customer_comment')

    def clean_image(self):
        image = self.cleaned_data['image']
        if not image and not self.instance.pk:
            raise ValidationError('Добавьте фотографию товара')
        return image

    def clean_place(self):
        value = self.cleaned_data['place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def clean_price(self):
        price = self.cleaned_data['price']
        if not price or price < 0:
            raise ValidationError('Цена не может быть нулевой или меньше 0')
        return price

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        if self.instance.pk and self.instance.product.pk and self.instance.product.shopping_type == ShoppingTypes.JOINT:
            prev_value = self.instance.quantity
            self.joint_quantity_delta = value - prev_value
            product = self.instance.product
            if (product.quantity - self.joint_quantity_delta) < 0:
                raise ValidationError(
                    'Указанное количество ({}) больше доступного ({})'.format(value, product.quantity))
        return value

    @transaction.atomic
    def save(self, commit=True):
        if self.instance.pk:
            product = self.instance.product
            if product:
                place = self.cleaned_data.get('place')
                if place:
                    product.place = place
                name = self.cleaned_data.get('name', '')
                if name:
                    product.name = name
                price = self.cleaned_data.get('price')
                if price:
                    product.price = price
                if product.shopping_type == ShoppingTypes.JOINT:
                    product.quantity -= self.joint_quantity_delta
                    product.save(update_fields=('place', 'name', 'price', 'quantity'))
                else:
                    product.save(update_fields=('place', 'name', 'price'))
        else:
            # in case when new order item is created
            self.instance.order = Order.objects.get(pk=self.order_id)
            product = Product(image=self.cleaned_data['image'],
                              created_by=self.user,
                              updated_by=self.user,
                              place=self.cleaned_data.get('place', ''),
                              name=self.cleaned_data.get('name', ''),
                              price=self.cleaned_data.get('price', 0))
            product.save()
            self.instance.product = product

        if self.parent_item:
            self.instance.parent = self.parent_item

        if (self.parent_item and self.parent_item.status != OrderItemStatuses.NOT_BAUGHT_OUT and
                self.instance.status != OrderItemStatuses.BAUGHT_OUT):
            self.instance.state = OrderItemStates.NOT_ACTIVE

        if self.instance.status == OrderItemStatuses.BAUGHT_OUT:
            self.instance.state = OrderItemStates.USED

            def _update_replacement_state(parent):
                if hasattr(parent, 'orderitem'):
                    replacement = parent.orderitem
                    if replacement.status != OrderItemStatuses.BAUGHT_OUT:
                        replacement.state = OrderItemStates.NOT_ACTIVE
                        replacement.status = OrderItemStatuses.CREATED
                        replacement.save()
                    _update_replacement_state(replacement)

            _update_replacement_state(self.instance)

        if self.instance.status == OrderItemStatuses.NOT_BAUGHT_OUT:
            self.instance.state = OrderItemStates.ACTIVE
            if hasattr(self.instance, 'orderitem'):
                replacement_item = self.instance.orderitem
                replacement_item.state = OrderItemStates.USED
                replacement_item.save()

        # Update statuses for other joint items
        if self.instance.pk and self.instance.product.pk and self.instance.product.shopping_type == ShoppingTypes.JOINT:
            for oi in product.orderitem_set.all():
                if self.instance.status != oi.status:
                    if self.instance.status == OrderItemStatuses.BAUGHT_OUT:
                        oi.status = OrderItemStatuses.BAUGHT_OUT
                        oi.state = OrderItemStates.USED
                    elif self.instance.status == OrderItemStatuses.NOT_BAUGHT_OUT:
                        oi.status = OrderItemStatuses.NOT_BAUGHT_OUT
                        oi.state = OrderItemStates.ACTIVE
                    else:
                        oi.status = OrderItemStatuses.CREATED
                        oi.state = OrderItemStates.USED
                    oi.save()

        self.instance = super().save(commit=commit)
        if self.instance.pk:
            product = self.instance.product
            if product:
                product.update_order_price()
            else:
                self.instance.order.update_actual_price_with_user_balance()
        return self.instance


class JointItemToOrderForm(WithUserDataUpdateFormMixin, forms.ModelForm):

    def __init__(self, **kwargs):
        self.order = None
        self.product = None
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        order_id = kwargs.pop('order_id', None)
        if order_id:
            self.order = Order.objects.get(pk=order_id)
        product_id = kwargs.pop('product_id', None)
        if product_id:
            self.product = Product.objects.get(pk=product_id)
        super().__init__(**kwargs)

    class Meta:
        model = OrderItem
        fields = ('quantity', 'order_comment', 'customer_comment')

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        if value > self.product.quantity:
            raise ValidationError('Указанное количество ({}) больше доступного ({})'
                                  .format(value, self.product.quantity))
        if not self.product.quantity:
            raise ValidationError('Не осталось свободного товара')
        return value

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            if not self.order:
                self.order = Order(created_by=self.user, updated_by=self.user)
                self.order.save()
            self.instance.order = self.order
            self.instance.product = self.product
            self.instance.state = OrderItemStates.ACTIVE
            self.product.quantity -= self.cleaned_data['quantity']
            self.product.save()

            if self.product.quantity == 0:
                # update all order items states
                self.product.orderitem_set.all().update(state=OrderItemStates.USED)
                self.instance.state = OrderItemStates.USED

        self.instance = super().save(commit=commit)

        if self.instance.pk:
            self.instance.product.update_order_price()
        return self.instance


class ProductForm(WithUserDataUpdateFormMixin, forms.ModelForm):
    image = forms.ImageField(label='Фото товара', required=False)
    comment = forms.CharField(label='Комментарий к товару', required=False, widget=forms.widgets.Textarea)

    class Meta:
        model = Product
        fields = ('image', 'name', 'place', 'price', 'quantity', 'comment', 'shopping_type')

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(**kwargs)
        # TODO: remove if another shopping_type is necessary
        self.fields.pop('shopping_type')

    def clean_image(self):
        image = self.cleaned_data['image']
        if not image:
            raise ValidationError('Добавьте фото товара')
        return image

    def clean_place(self):
        value = self.cleaned_data['place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def clean_price(self):
        value = self.cleaned_data['price']
        if value < 1:
            raise ValidationError('Цена должна быть больше 0')
        return value

    def save(self, commit=True):
        # TODO: remove if another shopping_type is necessary
        if self.instance.pk:
            if 'image' in self.changed_data:
                old_image = Product.objects.get(pk=self.instance.pk).image
                old_image.delete()
        else:
            self.instance.shopping_type = ShoppingTypes.JOINT
        return super().save(commit=True)


class SettingsForm(forms.Form):
    extra_charge = forms.DecimalField(label='Наценка в %',
                                      min_value=0.01, max_value=100,
                                      max_digits=5, decimal_places=2)
    announcement = forms.CharField(label='Объявление', max_length=300, widget=forms.Textarea, required=False)
    contacts = forms.CharField(label='Контакты', max_length=300, widget=forms.Textarea, required=False)
    partnership = forms.CharField(label='Сотрудничество', max_length=300, widget=forms.Textarea, required=False)
    work_schedule = forms.ImageField(label='Фото графика работы', required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields:
            field_val = self.fields[field]
            # if not isinstance(field_val, (forms.ImageField, forms.FileField)):
            field_val.initial = SettingOptionHandler(field).value

    def clean_extra_charge(self):
        value = self.cleaned_data['extra_charge']
        return str(value)

    def save(self):
        for setting in self.cleaned_data:
            instance = SettingOptionHandler(setting)
            instance.value = self.cleaned_data[setting]


class NewsForm(forms.Form):
    title = forms.CharField(label="Заголовок")
    content = forms.CharField(label="Новость", widget=forms.Textarea)

    class Meta:
        model = News
        fields = ('title', 'content', 'published')


class UserForm(forms.ModelForm):

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(**kwargs)
        self.fields['email'].disabled = True
        if self.user.role != Roles.ADMINISTRATOR:
            self.fields['role'].disabled = True
            self.fields['balance'].disabled = True

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'balance', 'birth_date', 'phone', 'delivery_address')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)
