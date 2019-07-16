from django.forms.widgets import ClearableFileInput, CheckboxInput, FILE_INPUT_CONTRADICTION


class ClearableMultiFileInput(ClearableFileInput):

    def __init__(self, *args, **kwargs):
        if 'attrs' in kwargs:
            kwargs['attrs'].update({'multiple': True})
        else:
            kwargs['attrs'] = {'multiple': True}
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        # upload = super().value_from_datadict(data, files, name)
        upload = files.getlist(name)
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        return upload
