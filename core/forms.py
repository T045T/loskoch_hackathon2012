from django import forms

from core.models import Flatshare


class FlatCreationForm(forms.ModelForm):
    class Meta:
        model = Flatshare
        fields = ['size', 'address', 'max_guests', 'name']
