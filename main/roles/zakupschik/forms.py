from django.forms import (
    ModelForm,
    BaseModelFormSet,
    BooleanField,
)
from django.forms import ValidationError
from django.db import transaction
from main.models import Product
from main.core.constants import OrderItemStatuses


class ZakupschikProductForm(ModelForm):
    status_baught_out = BooleanField(required=False)
    status_not_baught_out = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.orderitem_set.count():
            orderitem = self.instance.orderitem_set.first()
            if orderitem.status == OrderItemStatuses.BAUGHT_OUT:
                self.fields['status_baught_out'].initial = True
                self.fields['status_not_baught_out'].initial = False
            elif orderitem.status == OrderItemStatuses.NOT_BAUGHT_OUT:
                self.fields['status_baught_out'].initial = False
                self.fields['status_not_baught_out'].initial = True
            else:
                self.fields['status_baught_out'].initial = False
                self.fields['status_not_baught_out'].initial = False

    def clean(self):
        cleaned_data = super().clean()
        if ('status_baught_out' in cleaned_data and 'status_not_baught_out' in cleaned_data and
                cleaned_data['status_baught_out'] and cleaned_data['status_not_baught_out']):
            raise ValidationError('Только одна галочка должна быть выбрана')
        return cleaned_data

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.cleaned_data.get('status_baught_out'):
            for orderitem in self.instance.orderitems_for_baught_out:
                orderitem.status = OrderItemStatuses.BAUGHT_OUT
                orderitem.save()
        elif self.cleaned_data.get('status_not_baught_out'):
            for orderitem in self.instance.orderitems_for_baught_out:
                orderitem.status = OrderItemStatuses.NOT_BAUGHT_OUT
                orderitem.save()
        else:
            for orderitem in self.instance.orderitems_for_baught_out:
                orderitem.status = OrderItemStatuses.CREATED
                orderitem.save()
        return super().save(*args, **kwargs)

    @property
    def quantity(self):
        return sum(self.instance.orderitems_for_baught_out.values_list('quantity', flat=True))

    class Meta:
        model = Product
        fields = ('status_baught_out', 'status_not_baught_out')


class ZakupschikProductBaseFormSet(BaseModelFormSet):

    def clean(self):
        super().clean()
        for form in self.forms:
            if form.is_valid():
                form.save()
