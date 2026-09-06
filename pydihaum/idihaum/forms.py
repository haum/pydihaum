# -*- coding: utf-8 -*-
from django import forms

from .models import Card, User


class MembreForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'active']
        labels = {'name': 'Nom', 'active': 'Actif'}


class CarteForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['uid', 'label', 'user', 'active']
        labels = {
            'uid': 'UID de la carte',
            'label': 'Libellé',
            'user': 'Membre',
            'active': 'Active',
        }
        help_texts = {
            'uid': "Identifiant lu par le lecteur. Le journal des passages "
                   "affiche les UID inconnus : badger une carte neuve permet "
                   "de relever le sien.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Un membre inactif reste proposé s'il est déjà associé : on ne veut pas
        # qu'une modification de libellé casse silencieusement l'association.
        self.fields['user'].queryset = User.objects.order_by('name')

    def clean_uid(self):
        uid = (self.cleaned_data['uid'] or '').strip()
        if not uid:
            raise forms.ValidationError("L'UID ne peut pas être vide.")
        doublon = Card.objects.filter(uid=uid)
        if self.instance.pk:
            doublon = doublon.exclude(pk=self.instance.pk)
        if doublon.exists():
            raise forms.ValidationError("Cet UID est déjà attribué à une autre carte.")
        return uid
