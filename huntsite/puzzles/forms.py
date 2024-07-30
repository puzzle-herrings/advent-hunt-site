from crispy_bulma.layout import FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.urls import reverse


class GuessForm(forms.Form):
    guess = forms.CharField(
        label="",
        help_text="",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "input", "style": "min-width: 24em;"}),
    )

    def __init__(self, *args, slug: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "guess-form"
        self.helper.form_method = "post"
        self.helper.form_action = reverse("guess_submit", kwargs={"slug": slug})
        self.helper.attrs = {
            "hx-post": reverse("guess_submit", kwargs={"slug": slug}),
            "hx-target": "#guesses-table",
            "hx-on::after-request": " if(event.detail.successful) this.reset()",
        }
        self.helper.layout = Layout(
            FormGroup(
                Field("guess"),
                Submit("submit", "Submit", css_class="is-primary"),
            )
        )
