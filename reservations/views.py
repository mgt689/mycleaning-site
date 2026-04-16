from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import DemandeForm
from .models import Avis, Photo
import logging

logger = logging.getLogger(__name__)

def accueil(request):
    """Vue pour la page d'accueil avec avis et photos"""
    avis = Avis.objects.filter(publie=True)  # Tous les avis publiés
    photos = Photo.objects.filter(affichee=True)
    
    context = {
        'avis': avis,
        'photos': photos,
    }
    return render(request, 'reservations/accueil.html', context)


def faire_demande(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            # 1. Sauvegarde
            nouvelle_demande = form.save() 

            date_souhaitee_txt = (
                nouvelle_demande.date_souhaitee.strftime("%d/%m/%Y")
                if nouvelle_demande.date_souhaitee
                else "Non précisée"
            )
            
            # 2. EMAIL À L'ADMIN
            sujet_admin = f"🔔 NOUVELLE DEMANDE : {nouvelle_demande.get_type_prestation_display()} à Auxerre"
            message_admin = f"""Bonjour l'équipe MyCleaning,

Une nouvelle demande de devis vient d'être déposée sur le site !

Détails du client :
- Nom : {nouvelle_demande.nom}
- Email : {nouvelle_demande.email}
- Téléphone : {nouvelle_demande.numero_telephone}
- Prestation : {nouvelle_demande.get_type_prestation_display()}
- Surface : {nouvelle_demande.surface}m²
- Date souhaitée : {date_souhaitee_txt}
- Adresse : {nouvelle_demande.rue}, {nouvelle_demande.code_postal} {nouvelle_demande.ville}

Connectez-vous sur votre espace administrateur pour voir les détails :
https://mycleaning-sites-4vyvg.ondigitalocean.app/admin/

Le système automatique MyCleaning."""
            try:
                send_mail(
                    sujet_admin,
                    message_admin,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                logger.info(f"Email admin envoyé avec succès pour {nouvelle_demande.nom}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du mail admin: {str(e)}")
                # On continue même si l'email échoue
            
            # 3. EMAIL DE CONFIRMATION AU CLIENT
            sujet_client = "✅ Votre demande de devis MyCleaning a été reçue"
            message_client = f"""Bonjour {nouvelle_demande.nom},

Merci d'avoir soumis votre demande de devis sur MyCleaning !

Résumé de votre demande :
- Prestation : {nouvelle_demande.get_type_prestation_display()}
- Surface : {nouvelle_demande.surface}m²
- Date souhaitée : {date_souhaitee_txt}
- Adresse : {nouvelle_demande.rue}, {nouvelle_demande.code_postal} {nouvelle_demande.ville}

Notre équipe examinera votre demande et vous recontactera sous peu au {nouvelle_demande.numero_telephone}.

Cordialement,
L'équipe MyCleaning
contact@mycleaning.studio"""
            try:
                send_mail(
                    sujet_client,
                    message_client,
                    settings.DEFAULT_FROM_EMAIL,
                    [nouvelle_demande.email],
                    fail_silently=False,
                )
                logger.info(f"Email confirmation envoyé à {nouvelle_demande.email}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du mail client: {str(e)}")
                # On continue même si l'email échoue

            # 4. REDIRECTION (Très important pour éviter l'erreur !)
            return redirect('demande_succes')

    else:
        # Si on arrive sur la page la première fois (GET)
        form = DemandeForm()

    # 5. AFFICHAGE (Si le formulaire n'est pas valide ou si c'est la 1ère visite)
    return render(request, 'reservations/demande.html', {'form': form})


def demande_succes(request):
    return render(request, 'reservations/succes.html')