from decimal import Decimal

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
    VAT_RATE_CHOICES = (
        ("6", "6% BTW — woning minstens 10 jaar in gebruik"),
        ("21", "21% BTW — standaardtarief"),
    )

    name = forms.CharField(max_length=120, label="Naam", error_messages={"required": "Vul uw naam in."})
    email = forms.EmailField(label="E-mailadres", error_messages={"required": "Vul uw e-mailadres in.", "invalid": "Vul een geldig e-mailadres in."})
    thickness = forms.DecimalField(
        required=False,
        min_value=Decimal("0.1"),
        max_value=99,
        decimal_places=1,
        label="Dikte (cm)",
        error_messages={
            "invalid": "Vul de dikte in als een getal, bijvoorbeeld 7,5.",
            "min_value": "De dikte van de chape moet groter zijn dan 0 cm.",
            "max_value": "De dikte van de chape mag maximaal 99 cm zijn.",
        },
    )
    area = forms.DecimalField(
        required=False,
        min_value=1,
        decimal_places=1,
        label="Oppervlakte (m²)",
        error_messages={
            "invalid": "Vul de oppervlakte in als een getal.",
            "min_value": "De oppervlakte moet minstens 1 m² zijn.",
        },
    )
    floor_heating = forms.CharField(required=False, max_length=120, label="Vloerverwarming")
    vat_rate = forms.ChoiceField(
        choices=VAT_RATE_CHOICES,
        label="BTW-tarief",
        error_messages={
            "required": "Kies het toepasselijke BTW-tarief.",
            "invalid_choice": "Kies 6%% of 21%% BTW.",
        },
    )
    address = forms.CharField(max_length=240, label="Werfadres", error_messages={"required": "Vul het werfadres in."})
    message = forms.CharField(widget=forms.Textarea, max_length=4000, label="Bericht", error_messages={"required": "Beschrijf kort uw aanvraag."})
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Ongeldige aanvraag.")
        return ""
