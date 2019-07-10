from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models as m_models


# Register your models here.
admin.site.register(m_models.Provider)
admin.site.register(m_models.User, UserAdmin)
admin.site.register(m_models.Order)
