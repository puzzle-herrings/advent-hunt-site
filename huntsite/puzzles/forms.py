from crispy_bulma.layout import HTML, FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms


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
        self.helper.attrs = {
            "hx-post": ".",
            "hx-target": "#guesses-table",
            "hx-on::after-request": "if(event.detail.successful) this.reset()",
        }
        self.helper.layout = Layout(
            FormGroup(
                Field("guess"),
                Submit("submit", "Submit", css_class="is-primary"),
                HTML('<p class="htmx-indicator is-size-4 rotate">❄</p>'),
                css_class="is-align-items-center",
            )
        )
