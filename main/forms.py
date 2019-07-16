from django import forms
from .models import Provider, Order


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
    images = forms.ImageField(label='Изображение товара',
                              widget=forms.widgets.ClearableFileInput(attrs={'multiple': True}))
    # place = forms.CharField()
    # price = forms.DecimalField()
    # quantity = forms.IntegerField()
    order_comment = forms.CharField(widget=forms.Textarea)
    customer_comment = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Order
        fields = ('images', 'place', 'order_comment', 'customer_comment', 'price', 'quantity')

    def clean(self):
        return self.cleaned_data



