from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import DemandeForm

def faire_demande(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            # 1. Sauvegarde
            nouvelle_demande = form.save() 
            
            # 2. Préparation de l'email
            sujet = f"🔔 NOUVELLE DEMANDE : {nouvelle_demande.get_type_prestation_display()} à Auxerre"
            message = f"""
Bonjour l'équipe MyCleaning,

Une nouvelle demande de devis vient d'être déposée sur le site !

Détails du client :
- Nom : {nouvelle_demande.nom}
- Téléphone : {nouvelle_demande.numero_telephone}
- Prestation : {nouvelle_demande.get_type_prestation_display()}

Connectez-vous sur votre espace administrateur pour voir les détails :
http://127.0.0.1:8000/admin/

Le système automatique MyCleaning.
"""
            # 3. Envoi de l'email
            send_mail(
                sujet,
                message,
                'ne-pas-repondre@mycleaning.fr', 
                ['contact-admin@mycleaning.fr'],
                fail_silently=False,
            )

            # 4. REDIRECTION (Très important pour éviter l'erreur !)
            return redirect('demande_succes')

    else:
        # Si on arrive sur la page la première fois (GET)
        form = DemandeForm()

    # 5. AFFICHAGE (Si le formulaire n'est pas valide ou si c'est la 1ère visite)
    return render(request, 'reservations/demande.html', {'form': form})


def demande_succes(request):
    return render(request, 'reservations/succes.html')