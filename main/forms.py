from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
    Provider,
    Order,
    OrderItem,
    Product,
    User
)
from main.core import widgets as custom_widgets, form_fields as custom_form_fields
from main.core.constants import Roles, OrderStatuses, ShoppingTypes, OrderItemStates, OrderItemStatuses


class ProviderForm(forms.ModelForm):
    name = forms.CharField(label='Имя', help_text='Имя поставщика')
    vk_link = forms.CharField(label='Ссылка Вконтакте', help_text='URL профиля Вконтакте')
    place = forms.CharField(label='Место', help_text='Номер места поставщика')
    description = forms.CharField(label='Описание', widget=forms.Textarea, help_text='Описание с данными поставщика')
    picture = forms.CharField(label='Изображение', help_text='URL либо путь к картинке')
    product_type = forms.CharField(label='Чем торгует', help_text='Вид товара')

    class Meta:
        model = Provider
        exclude = []


class NewOrderForm(forms.ModelForm):
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

        if not self.instance.created_by:
            self.instance.created_by = self.user
        self.instance.updated_by = self.user
        self.instance.save()

        order_items = []
        for image in self.cleaned_data['images']:
            product = Product(image=image, created_by=self.user, updated_by=self.user)
            product.save()
            # order_item = OrderItem(order=self.instance, product=product, created_by=self.user, updated_by=self.user)
            # order_item.save()
            # to optimize with bulk create
            order_items.append(OrderItem(order=self.instance, product=product, created_by=self.user, updated_by=self.user))
        if order_items:
            OrderItem.objects.bulk_create(order_items)
        return self.instance


class OrderForm(forms.ModelForm):
    images = custom_form_fields.MultipleFilesField(label='Изображение товара',
                                                   widget=custom_widgets.ClearableMultiFileInput())
    status = forms.ChoiceField(required=False, choices=tuple(OrderStatuses))

    class Meta:
        model = Order
        fields = ('images', 'status', 'paid_price')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_balance_delta = 0
        super().__init__(*args, **kwargs)

        if getattr(self.user, 'role', Roles.UNREGISTERED) not in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            self.fields.pop('status')

    @transaction.atomic
    def pay_order(self):
        self.instance.status = OrderStatuses.PAYING_TO_BE_CONFIRMED
        user = self.instance.created_by
        user.balance -= self.instance.price
        user.save()
        self.instance.save()

    def clean_paid_price(self):
        paid_price = self.cleaned_data['paid_price']
        return paid_price if paid_price else 0

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.instance.pk:
            paid_price = cleaned_data['paid_price']
            cleaned_data['paid_price'] = self.instance.paid_price + paid_price
            self.user_balance_delta = paid_price
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = self.instance.created_by
        user.balance += self.user_balance_delta
        user.save()
        return super().save(commit=True)


class OrderItemForm(forms.ModelForm):
    product_image = forms.ImageField(label='Изображение товара', required=False)
    product_place = forms.CharField(label='Место')
    product_name = forms.CharField(label='Название товара', required=False)

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        self.parent_item = kwargs.pop('parent_item', None)
        super().__init__(**kwargs)

        self.fields['product_name'].initial = self.instance.product_name
        self.fields['product_place'].initial = self.instance.product_place
        if self.is_image_update_forbidden:
            self.fields.pop('product_image')
        if self.user and self.user.role == Roles.ZAKAZSCHIK:
            self.fields.pop('status')

    class Meta:
        model = OrderItem
        fields = ('product_image',
                  'product_name',
                  'product_place',
                  'price',
                  'quantity',
                  'status',
                  'order_comment',
                  'customer_comment')

    def clean_product_image(self):
        image = self.cleaned_data['product_image']
        if not image and not self.instance.pk:
            raise ValidationError('Добавьте фотографию товара')
        return image

    def clean_product_place(self):
        value = self.cleaned_data['product_place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def clean_price(self):
        price = self.cleaned_data['price']
        if not price or price < 0:
            raise ValidationError('Цена не может быть нулевой или меньше 0')
        return price

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
            product = Product(image=self.cleaned_data['product_image'],
                              created_by=self.user,
                              updated_by=self.user,
                              place=self.cleaned_data.get('product_place', ''),
                              name=self.cleaned_data.get('product_name', ''))
            product.save()
            self.instance.product = product
        else:
            place = self.cleaned_data.get('product_place')
            product = self.instance.product
            if product:
                if place:
                    product.place = place
                name = self.cleaned_data.get('product_name', '')
                if name:
                    product.name = name
                product.save(update_fields=('place', 'name'))

        if self.parent_item:
            self.instance.parent = self.parent_item

        if (self.parent_item and self.parent_item.status != OrderItemStatuses.NOT_BAUGHT_OUT and
                self.instance.status != OrderItemStatuses.BAUGHT_OUT):
            self.instance.state = OrderItemStates.NOT_ACTIVE

        if self.instance.status == OrderItemStatuses.NOT_BAUGHT_OUT:
            self.instance.state = OrderItemStates.ACTIVE
            replacement_item = self.instance.replacement
            if replacement_item:
                replacement_item.state = OrderItemStates.USED
                replacement_item.save()

        return super().save(commit=commit)


class JointOrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.get_joint_products(), label='Совместный товар', widget=forms.widgets.Select())

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        super().__init__(**kwargs)

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity', 'status', 'order_comment', 'customer_comment')

    def clean_product_place(self):
        value = self.cleaned_data['product_place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['price'] = cleaned_data['product'].price
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
            # product = Product(image=self.cleaned_data['product_image'], created_by=self.user, updated_by=self.user)
            # product.save()
            # self.instance.product = product
        return super().save(commit=commit)


class JointItemToOrderForm(forms.ModelForm):


    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.product_id = kwargs.pop('product_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        super().__init__(**kwargs)
        # self.fields['product'].choices = Product.objects.all()
        # self.fields['product'].queryset = Product.objects.all()
        print(self.product_id)

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity', 'status', 'order_comment', 'customer_comment')

    def clean_product_place(self):
        value = self.cleaned_data['product_place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['price'] = cleaned_data['product'].price
        print(cleaned_data)
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
            # product = Product(image=self.cleaned_data['product_image'], created_by=self.user, updated_by=self.user)
            # product.save()
            self.instance.product = Product.objects.get(pk=self.product_id)
        return super().save(commit=commit)


class ProductForm(forms.ModelForm):

    comment = forms.CharField(label='Комментарий к товару', required=False, widget=forms.widgets.Textarea)

    class Meta:
        model = Product
        fields = ('image', 'name', 'place', 'price', 'quantity', 'comment', 'shopping_type')

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(**kwargs)
        #TODO: remove if another shopping_type is necessary
        self.fields.pop('shopping_type')

    def clean_place(self):
        value = self.cleaned_data['place'].strip().replace(' ', '')
        if not value:
            raise ValidationError('Укажите, пожалуйста, номер места')
        return value

    def save(self, commit=True):
        # TODO: remove if another shopping_type is necessary
        if not self.instance.pk:
            self.instance.shopping_type = ShoppingTypes.JOINT
        return super().save(commit=True)


class UserForm(forms.ModelForm):

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(**kwargs)
        if self.user.role != Roles.ADMINISTRATOR:
            self.fields.pop('role')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'phone', 'location', 'role')
