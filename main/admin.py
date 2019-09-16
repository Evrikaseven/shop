from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models as m_models
from . import forms


class CustomUserAdmin(UserAdmin):
    add_form = forms.CustomUserCreationForm
    form = forms.CustomUserChangeForm
    model = m_models.User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


# Register your models here.
admin.site.register(m_models.Provider)
admin.site.register(m_models.User, CustomUserAdmin)
admin.site.register(m_models.Order)
