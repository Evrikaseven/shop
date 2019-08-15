

class WithUserDataUpdateFormMixin:

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.user
        else:
            self.instance.created_by = self.user
            self.instance.updated_by = self.user
        return super().save(*args, **kwargs)
