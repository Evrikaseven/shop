from django import forms
from django.db import transaction
from .models import Provider, Order, OrderImage
from main.core import widgets as custom_widgets, form_fields as custom_form_fields


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
    # place = forms.CharField()
    # price = forms.DecimalField()
    # quantity = forms.IntegerField()
    order_comment = forms.CharField(widget=forms.Textarea)
    customer_comment = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Order
        fields = ('images', 'place', 'order_comment', 'customer_comment', 'price', 'quantity')

    def clean_place(self):
        value = self.cleaned_data['place']
        return value.strip().replace(' ', '')

    @transaction.atomic
    def save(self, commit=True):
        if self.instance.pk:
            # Here check for existing images
            pass

        instance = super().save(commit=commit)
        for image in self.cleaned_data['images']:
            img = OrderImage(image=image, order=instance)
            img.save()
        return instance



