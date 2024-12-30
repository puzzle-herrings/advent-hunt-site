from crispy_bulma.layout import HTML, FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms


class GuessForm(forms.Form):
    guess = forms.CharField(
        label="",
        help_text="",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "input"}),
    )

    def __init__(self, *args, slug: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "guess-form"
        self.helper.attrs = {
            "hx-post": ".",
            "hx-target": "#guesses-results",
            "hx-on::after-request": "if(event.detail.successful) this.reset()",
        }
        self.helper.layout = Layout(
            FormGroup(
                Field("guess"),
                Submit("submit", "Submit", css_class="is-primary"),
                HTML(
                    '<div class="pseudorelative-outer">'
                    '<p class="htmx-indicator pseudorelative-inner loading-indicator is-size-4">'
                    "❄"
                    "</p>"
                    "</div>"
                ),
                css_class="is-align-items-center",
            )
        )
