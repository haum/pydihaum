# -*- coding: utf-8 -*-
"""Interface de gestion du contrôle d'accès.

Toutes les vues exigent une session authentifiée (comptes django.contrib.auth,
les mêmes que /admin). Rien n'est jamais supprimé : les modèles se désactivent.
Card.user est en DO_NOTHING, supprimer un membre laisserait des cartes pointant
vers un identifiant disparu — d'où le choix de l'activation/désactivation.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import door
from .forms import CarteForm, MembreForm
from .models import Card, Log, User

PAR_PAGE = 40

# Les trois listes se filtrent par le même paramètre `etat`, dont chacune définit
# les valeurs admises. Une valeur inconnue retombe sur la première (« tout »),
# ce qui rend l'URL infalsifiable sans avoir à la valider ailleurs.
ETATS_MEMBRES = ('tous', 'actifs', 'inactifs', 'sans-carte')
ETATS_CARTES = ('toutes', 'actives', 'inactives', 'bloquees')
ETATS_JOURNAL = ('tous', 'refus', 'inconnues', 'manuel')

# Le journal repère les refus au commentaire écrit par mqtt.py ; il n'existe pas
# de colonne d'état. Ces trois prédicats servent au filtre et à son effectif.
J_REFUS = Q(comment__startswith='Denied')
J_INCONNUES = Q(unknown_card__isnull=False) & ~Q(unknown_card='')
J_MANUEL = Q(comment__startswith='Ouverture manuelle')


def _tri_naturel(queryset, champ):
    """Trie en respectant les nombres : 2 avant 10, et « 15 (Staff) » avec les 15.

    Les libellés de cartes sont des numéros de badge, parfois suivis d'une
    précision. Un tri alphabétique donnerait 1, 10, 100, 11, 2 — inutilisable.
    CAST(... AS INTEGER) rend le préfixe numérique (0 s'il n'y en a pas), et le
    drapeau `est_texte` renvoie les libellés purement alphabétiques après les
    numéros plutôt que de les mélanger au rang 0.
    """
    return queryset.annotate(
        est_texte=Case(When(**{f'{champ}__regex': r'^[0-9]'}, then=Value(0)),
                       default=Value(1), output_field=IntegerField()),
        prefixe_num=Cast(champ, IntegerField()),
    ).order_by('est_texte', 'prefixe_num', champ)


def _page(request, queryset):
    return Paginator(queryset, PAR_PAGE).get_page(request.GET.get('page'))


def _params(request):
    """La requête courante sans `page`, pour que la pagination garde le filtre."""
    reste = request.GET.copy()
    reste.pop('page', None)
    return reste.urlencode()


def _etat(request, admis):
    demande = request.GET.get('etat') or admis[0]
    return demande if demande in admis else admis[0]


def _puces(defs, courant):
    """Prépare la barre de filtres : (clé, libellé, effectif, à signaler)."""
    return [{'cle': cle, 'libelle': libelle, 'nombre': nombre,
             'alerte': alerte and nombre, 'choisie': cle == courant}
            for cle, libelle, nombre, alerte in defs]


def _retour(request, defaut):
    """Où revenir après une bascule d'état.

    Le gabarit renvoie l'URL courante complète, filtre et pagination compris, pour
    qu'on ne perde pas sa place. Comme elle transite par le POST, on vérifie qu'elle
    reste sur cet hôte : sans ce contrôle, un formulaire forgé ferait de cette vue
    une redirection ouverte.
    """
    url = request.POST.get('retour') or ''
    if url and url_has_allowed_host_and_scheme(
            url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return url
    return defaut


@login_required
def tableau_de_bord(request):
    depuis = timezone.now() - timezone.timedelta(days=7)
    return render(request, 'idihaum/tableau_de_bord.html', {
        'nb_membres': User.objects.filter(active=True).count(),
        'nb_membres_inactifs': User.objects.filter(active=False).count(),
        'nb_cartes': Card.objects.filter(active=True).count(),
        'nb_cartes_inactives': Card.objects.filter(active=False).count(),
        'nb_passages_semaine': Log.objects.filter(created_at__gte=depuis).count(),
        'derniers': Log.objects.select_related('user', 'card').order_by('-created_at')[:12],
        'porte_reelle': door.porte_reelle(),
        'topic': door.topic_strike(),
    })


@login_required
def membres(request):
    q = (request.GET.get('q') or '').strip()
    etat = _etat(request, ETATS_MEMBRES)

    # Les deux compteurs de cartes sont annotés une fois pour toutes : la colonne
    # les affiche sans repasser une requête par ligne, et le filtre « sans carte
    # active » se lit directement dessus.
    qs = _tri_naturel(User.objects.annotate(
        nb_cartes=Count('card', distinct=True),
        nb_cartes_actives=Count('card', filter=Q(card__active=True), distinct=True),
    ), 'name')
    if etat == 'actifs':
        qs = qs.filter(active=True)
    elif etat == 'inactifs':
        qs = qs.filter(active=False)
    elif etat == 'sans-carte':
        qs = qs.filter(active=True, nb_cartes_actives=0)
    if q:
        qs = qs.filter(name__icontains=q)

    compte = User.objects.aggregate(
        tous=Count('id'),
        actifs=Count('id', filter=Q(active=True)),
        inactifs=Count('id', filter=Q(active=False)))
    # Un membre actif dont aucune carte n'ouvre : il se présente devant la porte
    # en pensant être en règle. C'est le cas qu'on veut voir tout de suite.
    orphelins = User.objects.filter(active=True).exclude(card__active=True).count()

    return render(request, 'idihaum/membres.html', {
        'page': _page(request, qs), 'q': q, 'etat': etat, 'params': _params(request),
        'puces': _puces((
            ('tous', 'Tous', compte['tous'], False),
            ('actifs', 'Actifs', compte['actifs'], False),
            ('inactifs', 'Inactifs', compte['inactifs'], False),
            ('sans-carte', 'Sans carte active', orphelins, True),
        ), etat),
    })


@login_required
def membre_form(request, pk=None):
    membre = get_object_or_404(User, pk=pk) if pk else None
    form = MembreForm(request.POST or None, instance=membre)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        messages.success(request, f'Membre « {obj.name} » enregistré.')
        return redirect('idihaum:membres')
    return render(request, 'idihaum/membre_form.html', {
        'form': form,
        'membre': membre,
        'cartes': _tri_naturel(membre.card_set.all(), 'label') if membre else [],
    })


@login_required
@require_POST
def membre_bascule(request, pk):
    membre = get_object_or_404(User, pk=pk)
    membre.active = not membre.active
    membre.save()
    etat = 'réactivé' if membre.active else 'désactivé'
    messages.success(request, f'Membre « {membre.name} » {etat}.')
    return redirect(_retour(request, 'idihaum:membres'))


@login_required
def cartes(request):
    q = (request.GET.get('q') or '').strip()
    etat = _etat(request, ETATS_CARTES)

    qs = _tri_naturel(Card.objects.select_related('user'), 'label')
    if etat == 'actives':
        qs = qs.filter(active=True)
    elif etat == 'inactives':
        qs = qs.filter(active=False)
    elif etat == 'bloquees':
        qs = qs.filter(active=True, user__active=False)
    if q:
        qs = qs.filter(Q(uid__icontains=q) | Q(label__icontains=q) | Q(user__name__icontains=q))

    # « Bloquées » : mqtt.py refuse la carte d'un membre désactivé même quand la
    # carte est active (Denied: inactive user). Ces cartes affichent « active »
    # partout et n'ouvrent pas — c'est la première chose à regarder quand un
    # membre dit que son badge ne marche plus.
    compte = Card.objects.aggregate(
        toutes=Count('id'),
        actives=Count('id', filter=Q(active=True)),
        inactives=Count('id', filter=Q(active=False)),
        bloquees=Count('id', filter=Q(active=True, user__active=False)))

    return render(request, 'idihaum/cartes.html', {
        'page': _page(request, qs), 'q': q, 'etat': etat, 'params': _params(request),
        'puces': _puces((
            ('toutes', 'Toutes', compte['toutes'], False),
            ('actives', 'Actives', compte['actives'], False),
            ('inactives', 'Inactives', compte['inactives'], False),
            ('bloquees', 'Bloquées (membre inactif)', compte['bloquees'], True),
        ), etat),
    })


@login_required
def carte_form(request, pk=None):
    carte = get_object_or_404(Card, pk=pk) if pk else None
    # Pré-remplissage : depuis un UID inconnu du journal, ou depuis la fiche d'un
    # membre à qui on ajoute une carte.
    initial = {}
    if not carte:
        if request.GET.get('uid'):
            initial['uid'] = request.GET['uid']
        if request.GET.get('user'):
            initial['user'] = request.GET['user']
    retour = request.GET.get('retour') or request.POST.get('retour') or ''
    form = CarteForm(request.POST or None, instance=carte, initial=initial)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        messages.success(request, f'Carte « {obj.label or obj.uid} » enregistrée.')
        return redirect(_retour(request, 'idihaum:cartes'))
    return render(request, 'idihaum/carte_form.html',
                  {'form': form, 'carte': carte, 'retour': retour})


@login_required
@require_POST
def carte_bascule(request, pk):
    carte = get_object_or_404(Card, pk=pk)
    carte.active = not carte.active
    carte.save()
    etat = 'réactivée' if carte.active else 'désactivée'
    messages.success(request, f'Carte « {carte.label or carte.uid} » {etat}.')
    return redirect(_retour(request, 'idihaum:cartes'))


@login_required
def journal(request):
    q = (request.GET.get('q') or '').strip()
    etat = _etat(request, ETATS_JOURNAL)

    qs = Log.objects.select_related('user', 'card').order_by('-created_at')
    if etat == 'refus':
        qs = qs.filter(J_REFUS)
    elif etat == 'inconnues':
        qs = qs.filter(J_INCONNUES)
    elif etat == 'manuel':
        qs = qs.filter(J_MANUEL)
    if q:
        qs = qs.filter(Q(user__name__icontains=q) | Q(card__uid__icontains=q)
                       | Q(unknown_card__icontains=q) | Q(comment__icontains=q))

    compte = Log.objects.aggregate(
        tous=Count('id'),
        refus=Count('id', filter=J_REFUS),
        inconnues=Count('id', filter=J_INCONNUES),
        manuel=Count('id', filter=J_MANUEL))

    return render(request, 'idihaum/journal.html', {
        'page': _page(request, qs), 'q': q, 'etat': etat, 'params': _params(request),
        'puces': _puces((
            ('tous', 'Tout', compte['tous'], False),
            ('refus', 'Refus', compte['refus'], False),
            ('inconnues', 'Cartes inconnues', compte['inconnues'], False),
            ('manuel', 'Ouvertures manuelles', compte['manuel'], False),
        ), etat),
    })


@login_required
@require_POST
def ouvrir_porte(request):
    try:
        door.ouvrir(request.user)
    except Exception as e:
        messages.error(request, f"La porte n'a pas pu être ouverte : {e}. "
                                "Vérifier que le broker MQTT répond.")
    else:
        if door.porte_reelle():
            messages.success(request, 'Porte ouverte.')
        else:
            messages.warning(request, f'Environnement de test : message envoyé sur '
                                      f'« {door.topic_strike()} », la vraie porte n\'a pas bougé.')
    return redirect('idihaum:tableau_de_bord')
