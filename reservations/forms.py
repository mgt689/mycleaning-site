from django import forms
from .models import DemandeNettoyage
from django.core.exceptions import ValidationError

class DemandeForm(forms.ModelForm):
    class Meta:
        model = DemandeNettoyage
        fields = [
            'nom', 'email', 'numero_telephone', 'type_prestation', 'surface',
            'rue', 'code_postal', 'ville',
            'nombre_chambres', 'nombre_salons', 'nombre_bureaux', 'nombre_toilettes', 'materiel_sur_place'
        ]

    def clean_numero_telephone(self):
        numero = self.cleaned_data.get('numero_telephone').replace(" ", "")
        if len(numero) != 10:
            raise ValidationError("Le numéro doit faire exactement 10 chiffres.")
        return numero

    def clean_code_postal(self):
        cp = self.cleaned_data.get('code_postal').replace(" ", "")
        if len(cp) != 5 or not cp.isdigit():
            raise ValidationError("Le code postal doit contenir exactement 5 chiffres.")
        return cp