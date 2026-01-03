#context_processors.py
from userauths.models import TypeCustomPermission
from PB_Entreprise.models import Vehicule, VisiteTechnique, Entretien, Assurance, Vignette, Patente, Stationnement, Gerant
from django.utils import timezone
from datetime import date

def grouped_user_permissions(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    grouped_permissions = {}

    for category in TypeCustomPermission.objects.all():
        perms = category.cat_permis.filter(users=user)
        if perms.exists():
            grouped_permissions[category] = perms

    return {
        'grouped_permissions': grouped_permissions
    }

def alertes_count(request):
    """Calcule le nombre total d'alertes critiques pour l'affichage dans la navbar"""
    if not request.user.is_authenticated:
        return {'total_alertes': 0, 'alertes_list': []}
    
    user = request.user
    now = timezone.now()
    total_alertes = 0
    alertes_list = []
    
    # Filtrer les véhicules selon le type d'utilisateur
    if user.user_type == "4":
        try:
            gerant = user.gerants.get()
            if gerant.gerant_voiture:
                vehicules = Vehicule.objects.filter(category=gerant.gerant_voiture)
            else:
                vehicules = Vehicule.objects.none()
        except:
            vehicules = Vehicule.objects.none()
    else:
        vehicules = Vehicule.objects.all()
    
    # Parcourir tous les véhicules et compter les alertes critiques
    for vehicule in vehicules:
        # Visite technique
        visite = VisiteTechnique.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if visite and isinstance(visite.jour_restant, int) and 1 <= visite.jour_restant <= 32:
            total_alertes += 1
            alertes_list.append({
                'type': 'Visite technique',
                'vehicule': vehicule.immatriculation,
                'jours': visite.jour_restant
            })
        
        # Entretien
        entretien = Entretien.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if entretien and isinstance(entretien.jours_ent_restant, int) and 1 <= entretien.jours_ent_restant <= 3:
            total_alertes += 1
            alertes_list.append({
                'type': 'Entretien',
                'vehicule': vehicule.immatriculation,
                'jours': entretien.jours_ent_restant
            })
        
        # Assurance
        assurance = Assurance.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if assurance and isinstance(assurance.jours_assu_restant, int) and 1 <= assurance.jours_assu_restant <= 7:
            total_alertes += 1
            alertes_list.append({
                'type': 'Assurance',
                'vehicule': vehicule.immatriculation,
                'jours': assurance.jours_assu_restant
            })
        
        # Vignette
        vignette = Vignette.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if vignette and isinstance(vignette.jours_vign_restant, int) and 1 <= vignette.jours_vign_restant <= 10:
            total_alertes += 1
            alertes_list.append({
                'type': 'Vignette',
                'vehicule': vehicule.immatriculation,
                'jours': vignette.jours_vign_restant
            })
        
        # Patente
        patente = Patente.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if patente and isinstance(patente.jours_pate_restant, int) and 1 <= patente.jours_pate_restant <= 10:
            total_alertes += 1
            alertes_list.append({
                'type': 'Patente',
                'vehicule': vehicule.immatriculation,
                'jours': patente.jours_pate_restant
            })
        
        # Stationnement
        stationnement = Stationnement.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
        if stationnement and isinstance(stationnement.jours_cartsta_restant, int) and 1 <= stationnement.jours_cartsta_restant <= 10:
            total_alertes += 1
            alertes_list.append({
                'type': 'Stationnement',
                'vehicule': vehicule.immatriculation,
                'jours': stationnement.jours_cartsta_restant
            })
    
    return {
        'total_alertes': total_alertes,
        'alertes_list': alertes_list[:15]  # Limiter à 15 pour la navbar
    }
