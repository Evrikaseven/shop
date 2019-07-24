from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Provider, Order, OrderImage
from main.core import widgets as custom_widgets, form_fields as custom_form_fields
from main.core.constants import Roles


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


class OrderForm(forms.ModelForm):
    images = custom_form_fields.MultipleFilesField(required=False,
                                                   label='Изображение товара',
                                                   widget=custom_widgets.ClearableMultiFileInput())
    status = forms.ChoiceField(required=False, choices=Order.ORDER_STATUSES)

    class Meta:
        model = Order
        fields = ('images', 'place', 'price', 'quantity', 'order_comment', 'customer_comment', 'status')

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

    def clean_place(self):
        value = self.cleaned_data['place']
        return value.strip().replace(' ', '')

    @transaction.atomic
    def save(self, commit=True):
        super().save(commit=commit)

        if not self.instance.created_by:
            self.instance.created_by = self.user
        self.instance.updated_by = self.user
        self.instance.save()

        for image in self.cleaned_data['images']:
            img = OrderImage(image=image, order=self.instance)
            img.save()
        return self.instance



