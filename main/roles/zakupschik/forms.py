from django.forms import (
    ModelForm,
    BaseModelFormSet,
    BooleanField,
    ChoiceField,
)
from django.forms import ValidationError
from django.db import transaction
from main.models import Product
from main.core.constants import OrderItemStatuses


class ZakupschikProductForm(ModelForm):
    status = ChoiceField(choices=tuple(OrderItemStatuses), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.orderitem_set.count():
            orderitem = self.instance.orderitem_set.first()
            self.fields['status'].initial = orderitem.status

    def clean_status(self):
        value = int(self.cleaned_data.get('status'), OrderItemStatuses.CREATED)
        if value not in (OrderItemStatuses.CREATED, OrderItemStatuses.NOT_BAUGHT_OUT, OrderItemStatuses.BAUGHT_OUT):
            raise ValidationError('Статус имеет некорректное значение {value}'.format(value=value))
        return value

    @transaction.atomic
    def save(self, *args, **kwargs):
        status = self.cleaned_data.get('status')
        for orderitem in self.instance.orderitems_for_baught_out:
            orderitem.status = status
            orderitem.save()

    @property
    def quantity(self):
        return sum(self.instance.orderitems_for_baught_out.values_list('quantity', flat=True))

    class Meta:
        model = Product
        fields = ('status', )


class ZakupschikProductBaseFormSet(BaseModelFormSet):

    def clean(self):
        super().clean()
        for form in self.forms:
            if form.is_valid():
                form.save()
