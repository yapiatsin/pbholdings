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
    try:
        user = request.user
        total_alertes = 0
        alertes_list = []
        
        # Filtrer les véhicules selon le type d'utilisateur - TOUJOURS filtrer par car_statut=True
        if user.user_type == "4":
            try:
                gerant = Gerant.objects.get(user=user)
                categories_gerant = gerant.gerant_voiture.all()
                if categories_gerant.exists():
                    vehicules = Vehicule.objects.filter(category__in=categories_gerant, car_statut=True)
                else:
                    vehicules = Vehicule.objects.none()
            except (Gerant.DoesNotExist, Exception):
                vehicules = Vehicule.objects.none()
        else:
            # Filtrer aussi par car_statut=True pour tous les utilisateurs
            vehicules = Vehicule.objects.filter(car_statut=True)
        # Parcourir tous les véhicules et compter les alertes critiques
        for vehicule in vehicules:
            try:
                # Visite technique - utiliser order_by().first() pour compatibilité maximale
                visite = VisiteTechnique.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if visite:
                    try:
                        jours_restant = getattr(visite, 'jour_restant', None)
                        if jours_restant is not None and isinstance(jours_restant, int) and jours_restant <= 32:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Visite technique',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                
                # Entretien
                entretien = Entretien.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if entretien:
                    try:
                        jours_ent_restant = getattr(entretien, 'jours_ent_restant', None)
                        if jours_ent_restant is not None and isinstance(jours_ent_restant, int) and jours_ent_restant <= 3:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Entretien',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_ent_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                
                # Assurance
                assurance = Assurance.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if assurance:
                    try:
                        jours_assu_restant = getattr(assurance, 'jours_assu_restant', None)
                        if jours_assu_restant is not None and isinstance(jours_assu_restant, int) and jours_assu_restant <= 7:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Assurance',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_assu_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                
                # Vignette
                vignette = Vignette.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if vignette:
                    try:
                        jours_vign_restant = getattr(vignette, 'jours_vign_restant', None)
                        if jours_vign_restant is not None and isinstance(jours_vign_restant, int) and jours_vign_restant <= 10:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Vignette',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_vign_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                
                # Patente
                patente = Patente.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if patente:
                    try:
                        jours_pate_restant = getattr(patente, 'jours_pate_restant', None)
                        if jours_pate_restant is not None and isinstance(jours_pate_restant, int) and jours_pate_restant <= 10:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Patente',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_pate_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                
                # Stationnement
                stationnement = Stationnement.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if stationnement:
                    try:
                        jours_cartsta_restant = getattr(stationnement, 'jours_cartsta_restant', None)
                        if jours_cartsta_restant is not None and isinstance(jours_cartsta_restant, int) and jours_cartsta_restant <= 10:
                            total_alertes += 1
                            alertes_list.append({
                                'type': 'Stationnement',
                                'vehicule': vehicule.immatriculation,
                                'jours': jours_cartsta_restant
                            })
                    except (AttributeError, TypeError):
                        pass
                    
            except Exception:
                # En cas d'erreur sur un véhicule, continuer avec les autres
                continue
        
        return {
            'total_alertes': total_alertes,
            'alertes_list': alertes_list[:15]
        }
    
    except Exception:
        # En cas d'erreur générale, retourner des valeurs par défaut
        return {'total_alertes': 0, 'alertes_list': []}
