from allauth.account.forms import SignupForm as AllAuthSignupForm
from allauth.utils import set_form_field_order
from crispy_bulma.layout import FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout
from django import forms
from django.conf import settings
from turnstile.fields import TurnstileField

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
        if settings.USE_TURNSTILE:
            self.fields["turnstile"] = TurnstileField()

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


class TeamProfileUpdateForm(forms.Form):
    team_name = models.User.team_name.field.formfield()
    members = models.TeamProfile.members.field.formfield()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "team-profile-update-form"
        self.helper.attrs = {
            "hx-post": ".",
            "hx-target": "#team-profile-update-form",
            "hx-swap": "outerHTML",
        }
        self.helper.layout = Layout(
            Field("team_name"),
            Field("members"),
            FormGroup(
                Submit("save", "Save", css_class="is-primary"),
                HTML('<p class="htmx-indicator loading-indicator is-size-4">❄</p>'),
                css_class="is-align-items-center",
            ),
        )

    _SUCCESS_MESSAGE = '&nbsp;<i class="bi bi-check-circle"></i> Profile updated successfully.'
    _NO_CHANGES_MESSAGE = (
        '&nbsp;<i class="bi bi-exclamation-triangle"></i> You didn\'t enter any changes.'
    )

    def add_success_message(self):
        self.helper.layout[-1].fields.append(HTML(self._SUCCESS_MESSAGE))

    def add_no_changes_message(self):
        self.helper.layout[-1].fields.append(HTML(self._NO_CHANGES_MESSAGE))


class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "username-update-form"
        self.helper.layout.append(
            FormGroup(
                Submit("save", "Save", css_class="is-primary"),
                HTML('<p class="htmx-indicator loading-indicator is-size-4">❄</p>'),
                css_class="is-align-items-center",
            ),
        )
        self.helper.attrs = {
            "hx-post": ".",
            "hx-target": "#username-update-form",
            "hx-swap": "outerHTML",
        }

    _SUCCESS_MESSAGE = '&nbsp;<i class="bi bi-check-circle"></i> Username updated successfully.'
    _NO_CHANGES_MESSAGE = (
        '&nbsp;<i class="bi bi-exclamation-triangle"></i> You didn\'t enter any changes.'
    )

    def add_success_message(self):
        self.helper.layout[-1].fields.append(HTML(self._SUCCESS_MESSAGE))

    def add_no_changes_message(self):
        self.helper.layout[-1].fields.append(HTML(self._NO_CHANGES_MESSAGE))
