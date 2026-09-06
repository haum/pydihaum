"""Routage du projet pydihaum.

/admin reste l'administration Django de secours ; l'interface de gestion
quotidienne est servie par l'application idihaum à la racine.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='idihaum/connexion.html'), name='login'),
    # Django 5 n'accepte la déconnexion qu'en POST : le gabarit utilise un
    # formulaire, pas un lien.
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('idihaum.urls')),
]
