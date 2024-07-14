from allauth.account.forms import SignupForm as AllAuthSignupForm
from allauth.utils import set_form_field_order
from django import forms


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

    def save(self, request):
        user = super().save(request)
        user.team_name = self.cleaned_data["team_name"]
        user.save()
        return user
