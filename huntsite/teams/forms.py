from allauth.account.forms import SignupForm as AllAuthSignupForm
from allauth.utils import set_form_field_order
from crispy_bulma.layout import FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from django import forms
from django.forms import ModelForm

from huntsite.teams import models


class SignupForm(AllAuthSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "(Private) Used only for logging in."
        self.fields["team_name"] = forms.CharField(
            max_length=255,
            label="Team Name",
            help_text="(Public) How your team will be displayed.",
        )
        # Add team_name after username
        field_order = list(self.fields.keys())
        field_order.insert(field_order.index("username") + 1, "team_name")
        set_form_field_order(self, field_order)

    def clean(self):
        cleaned_data = super().clean()
        if models.User.objects.filter(team_name=cleaned_data["team_name"]).exists():
            self.add_error("team_name", "A team with that name already exists.")
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        user.team_name = self.cleaned_data["team_name"]
        user.save()
        return user


class AccountUpdateForm(ModelForm):
    class Meta:
        model = models.User
        fields = ["username", "team_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "account-update-form"
        self.helper.form_method = "post"
        self.helper.form_action = "."
        self.helper.layout.append(
            FormGroup(
                Submit("save", "Save", css_class="is-primary"), css_class="is-align-items-center"
            ),
        )
        self.helper.attrs = {
            "hx-post": ".",
            "hx-target": "#account-update-form",
            "hx-swap": "outerHTML",
        }

    _SUCCESS_MESSAGE = '&nbsp;<i class="bi bi-check-circle"></i> Account updated successfully.'

    def add_success_message(self):
        self.helper.layout[-1].fields.append(HTML(self._SUCCESS_MESSAGE))
