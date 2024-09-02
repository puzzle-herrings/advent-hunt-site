from django.contrib.admin import site

# Disable bulk delete by default
site.disable_action("delete_selected")


class UneditableAsReadOnlyAdminMixin:
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields if not field.editable]
        return []
