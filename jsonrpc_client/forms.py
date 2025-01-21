from django import forms


class InputForm(forms.Form):
    method = forms.CharField(
        required=True,
        label="Method",
        widget=forms.TextInput(attrs={"placeholder": "Enter method name"})
    )
    parameters = forms.CharField(
        required=True,
        label="Parameters",
        widget=forms.Textarea(attrs={"placeholder": "Enter parameters as JSON"})
    )
