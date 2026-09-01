from django import forms

from .models import SiteConfiguration


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = ("next_available",)
        labels = {"next_available": "Eerstvolgende beschikbare datum"}
        widgets = {
            "next_available": forms.DateInput(
                attrs={"type": "date", "class": "management-date"},
                format="%Y-%m-%d",
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["next_available"].input_formats = ["%Y-%m-%d"]


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, label="Naam")
    email = forms.EmailField(label="E-mailadres")
    thickness = forms.DecimalField(required=False, min_value=0, max_value=99, decimal_places=1, label="Dikte (cm)")
    area = forms.DecimalField(required=False, min_value=1, decimal_places=1, label="Oppervlakte (m²)")
    floor_heating = forms.CharField(required=False, max_length=120, label="Vloerverwarming")
    address = forms.CharField(max_length=240, label="Werfadres")
    message = forms.CharField(widget=forms.Textarea, max_length=4000, label="Bericht")
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")
    recaptcha_token = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Ongeldige aanvraag.")
        return ""
