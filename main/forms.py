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
from main.core.constants import Roles, OrderStatuses


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
    status = forms.ChoiceField(required=False, choices=Order.ORDER_STATUSES)

    class Meta:
        model = Order
        fields = ('images', 'status')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if getattr(self.user, 'role', Roles.UNREGISTERED) not in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            self.fields.pop('status')

        # if self.instance.pk:
        #     order = Order.objects.get(pk=self.instance.pk)
        #     self.fields['images'].initial = OrderImage.objects.filter(order=order)
        #     self.fields['images'].choices = OrderImage.objects.filter(order=order)
        #     self.fields['images'].queryset = OrderImage.objects.filter(order=order)

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

        for image in self.cleaned_data['images']:
            product = Product(image=image, created_by=self.user, updated_by=self.user)
            product.save()
            order_item = OrderItem(order=self.instance, product=product, created_by=self.user, updated_by=self.user)
            order_item.save()
        return self.instance


class OrderForm(forms.ModelForm):
    images = custom_form_fields.MultipleFilesField(label='Изображение товара',
                                                   widget=custom_widgets.ClearableMultiFileInput())
    status = forms.ChoiceField(required=False, choices=Order.ORDER_STATUSES)

    class Meta:
        model = Order
        fields = ('images', 'status')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if getattr(self.user, 'role', Roles.UNREGISTERED) not in (Roles.ZAKUPSCHIK, Roles.ADMINISTRATOR):
            self.fields.pop('status')

    def save(self, commit=True):
        if self.instance.pk:
            if 'status' in self.changed_data and int(self.cleaned_data.get('status', OrderStatuses.CREATED)) == OrderStatuses.PAID:
                self.instance.paid_price = self.instance.price
        return super().save(commit=commit)


class OrderItemForm(forms.ModelForm):
    product_image = forms.ImageField(label='Изображение товара', required=False)

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        super().__init__(**kwargs)
        if self.is_image_update_forbidden:
            self.fields.pop('product_image')

    class Meta:
        model = OrderItem
        fields = ('product_image', 'place', 'price', 'quantity', 'status', 'order_comment', 'customer_comment')

    def clean_product_image(self):
        image = self.cleaned_data['product_image']
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

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
            product = Product(image=self.cleaned_data['product_image'], created_by=self.user, updated_by=self.user)
            product.save()
            self.instance.product = product
        return super().save(commit=commit)


class JointOrderItemForm(forms.ModelForm):
    product = forms.ChoiceField(label='Совместный товар', )

    def __init__(self, **kwargs):
        self.order_id = kwargs.pop('order_id', None)
        self.user = kwargs.pop('user', None)
        self.is_image_update_forbidden = kwargs.pop('is_image_update_forbidden', None)
        super().__init__(**kwargs)

    class Meta:
        model = OrderItem
        fields = ('product', 'place', 'price', 'quantity', 'status', 'order_comment', 'customer_comment')

    def clean_product_image(self):
        image = self.cleaned_data['product_image']
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

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.order = Order.objects.get(pk=self.order_id)
            # product = Product(image=self.cleaned_data['product_image'], created_by=self.user, updated_by=self.user)
            # product.save()
            # self.instance.product = product
        return super().save(commit=commit)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'phone', 'location', 'role')
