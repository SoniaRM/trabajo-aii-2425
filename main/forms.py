#encoding:utf-8
from django import forms
from main.models import Clase, Rareza, Brawler

class BrawlerBusquedaForm(forms.Form):
    nombre = forms.CharField(label="Nombre del Brawler", widget=forms.TextInput(attrs={"class": "custom-input"}), required=True)

class FiltroAvanzadoForm(forms.Form):
    clase = forms.ModelChoiceField(
        queryset=Clase.objects.all(),
        required=False,
        label="Clase",
        empty_label="Todas las clases",
        widget=forms.Select(attrs={
            'class': 'custom-select',
        })
    )
    rareza = forms.ModelChoiceField(
        queryset=Rareza.objects.all(),
        required=False,
        label="Rareza",
        empty_label="Todas las rarezas",
        widget=forms.Select(attrs={
            'class': 'custom-select',
        })
    )
    winRate_min = forms.FloatField(
        required=False,
        label="Win Rate mínimo",
        widget=forms.NumberInput(attrs={"placeholder": "Ej: 0.5", "class": "custom-input"})
    )
    winRate_max = forms.FloatField(
        required=False,
        label="Win Rate máximo",
        widget=forms.NumberInput(attrs={"placeholder": "Ej: 1.0", "class": "custom-input"})
    )
    useRate_min = forms.FloatField(
        required=False,
        label="Use Rate mínimo",
        widget=forms.NumberInput(attrs={"placeholder": "Ej: 0.2", "class": "custom-input"})
    )
    useRate_max = forms.FloatField(
        required=False,
        label="Use Rate máximo",
        widget=forms.NumberInput(attrs={"placeholder": "Ej: 1.0", "class": "custom-input"})
    )
    selecciones_min = forms.IntegerField(
        required=False,
        label="Selecciones mínimas",
        widget=forms.NumberInput(attrs={"placeholder": "Ej: 100", "class": "custom-input"})
    )

class CompararBrawlersForm(forms.Form):
    brawler_1 = forms.ModelChoiceField(
        queryset=Brawler.objects.all(),
        label="Selecciona el primer Brawler",
        widget=forms.Select(attrs={
            'class': 'custom-select',
            'placeholder': 'Selecciona el primer Brawler'
        })
    )
    brawler_2 = forms.ModelChoiceField(
        queryset=Brawler.objects.all(),
        label="Selecciona el segundo Brawler",
        widget=forms.Select(attrs={
            'class': 'custom-select',
            'placeholder': 'Selecciona el segundo Brawler'
        })
    )