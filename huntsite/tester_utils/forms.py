from crispy_bulma.layout import FormGroup, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.urls import reverse


class TimeTravelForm(forms.Form):
    time_travel_to = forms.DateTimeField(
        label="Time Travel To",
        help_text="The time to travel to. This will affect the current time for the user.",
        input_formats=["%Y-%m-%d %H:%M:%S"],
        widget=forms.TextInput(attrs={"type": "datetime-local"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "time-travel-form"
        self.helper.form_method = "post"
        self.helper.attrs = {"hx-post": reverse("time_travel")}
        self.helper.layout = Layout(
            FormGroup(
                Field("time_travel_to"),
                Submit("submit", "Time Travel", css_class="is-primary"),
            )
        )
