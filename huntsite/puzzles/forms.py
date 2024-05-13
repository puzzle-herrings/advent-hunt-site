from django import forms


class GuessForm(forms.Form):
    guess = forms.CharField(
        label="",
        help_text="",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
