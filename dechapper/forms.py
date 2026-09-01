from django import forms


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

