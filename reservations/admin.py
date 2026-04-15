from django.contrib import admin
from .models import DemandeNettoyage, DemandeAcceptee

@admin.register(DemandeNettoyage)
class DemandeNettoyageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_prestation', 'statut', 'date_creation')
    list_filter = ('statut', 'type_prestation')
    
    # 1. On remplace 'adresse' par 'ville' dans la barre de recherche
    search_fields = ('nom', 'numero_telephone', 'ville')
    
    # 2. On met à jour l'ordre d'affichage dans la fiche client
    # On ajoute email, surface, rue, code_postal, ville, nombre_bureaux et on enlève adresse
    fields = (
        'nom', 'email', 'numero_telephone', 
        'surface', 'rue', 'code_postal', 'ville', 
        'type_prestation', 
        'nombre_chambres', 'nombre_salons', 'nombre_bureaux', 'nombre_toilettes', 
        'materiel_sur_place', 
        'statut', 'commentaire_admin'
    )

    def save_model(self, request, obj, form, change):
        if change and 'statut' in form.changed_data:
            sujet = f"Mise à jour de votre demande de nettoyage - {obj.get_statut_display()}"
            message_perso = obj.commentaire_admin if obj.commentaire_admin else "Pas de message supplémentaire."
            
            # ATTENTION : La ligne ci-dessous doit être alignée avec 'sujet'
            corps_email = f"""
Bonjour {obj.nom},

Votre demande de nettoyage pour un(e) {obj.get_type_prestation_display()} a été mise à jour.

Statut : {obj.get_statut_display()}

Message de notre équipe :
{message_perso}

Nous restons à votre disposition pour toute question.
L'équipe MyCleaning.
"""
            # Tout ce bloc doit aussi être aligné avec 'corps_email'
            from django.core.mail import send_mail
            send_mail(
                sujet,
                corps_email,
                'contact@mycleaning.studio',
                [obj.email],
                fail_silently=True,
            )

        # Cette ligne doit être alignée avec le 'if'
        super().save_model(request, obj, form, change)


@admin.register(DemandeAcceptee)
class DemandeAccepteeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_prestation', 'statut', 'date_creation')
    list_filter = ('statut', 'type_prestation')
    search_fields = ('nom', 'numero_telephone', 'ville')

    def get_queryset(self, request):
        # Cette fonction récupère toutes les demandes, puis les filtre
        qs = super().get_queryset(request)
        
        # ⚠️ TRÈS IMPORTANT : Remplace 'Confirmé' par le mot EXACT 
        # que tu as mis dans tes choix de statut (ex: 'Accepté', 'Valide', etc.)
        return qs.filter(statut='ACCEPTEE') 
