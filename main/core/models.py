from django.db import models
from django.conf import settings
# from django.utils import timezone


class ModelWithUser(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_created_by",
                                   null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_updated_by",
                                   null=True)

    class Meta:
        abstract = True


class ModelWithTimestamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
