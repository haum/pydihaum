# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'idihaum'

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('porte/ouvrir/', views.ouvrir_porte, name='ouvrir_porte'),

    path('membres/', views.membres, name='membres'),
    path('membres/nouveau/', views.membre_form, name='membre_nouveau'),
    path('membres/<int:pk>/', views.membre_form, name='membre_edition'),
    path('membres/<int:pk>/bascule/', views.membre_bascule, name='membre_bascule'),

    path('cartes/', views.cartes, name='cartes'),
    path('cartes/nouvelle/', views.carte_form, name='carte_nouvelle'),
    path('cartes/<int:pk>/', views.carte_form, name='carte_edition'),
    path('cartes/<int:pk>/bascule/', views.carte_bascule, name='carte_bascule'),

    path('journal/', views.journal, name='journal'),
]
