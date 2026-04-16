from django.contrib import admin, messages
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.text import slugify

from .models import DemandeNettoyage, DemandeAcceptee, Avis, Photo


@admin.register(DemandeNettoyage)
class DemandeNettoyageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_prestation', 'surface', 'prix_devis', 'date_souhaitee', 'statut', 'date_creation')
    list_filter = ('statut', 'type_prestation')
    actions = ['generer_devis_pdf']

    # 1. On remplace 'adresse' par 'ville' dans la barre de recherche
    search_fields = ('nom', 'numero_telephone', 'ville')

    # 2. On met à jour l'ordre d'affichage dans la fiche client
    fields = (
        'nom', 'email', 'numero_telephone',
        'surface', 'date_souhaitee', 'prix_devis',
        'rue', 'code_postal', 'ville',
        'type_prestation',
        'nombre_chambres', 'nombre_salons', 'nombre_bureaux', 'nombre_toilettes',
        'materiel_sur_place',
        'statut', 'commentaire_admin',
    )

    def generer_devis_pdf(self, request, queryset):
        """Génère un devis PDF pour UNE demande sélectionnée."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Sélectionnez une seule demande pour générer un devis PDF.",
                level=messages.ERROR,
            )
            return

        demande = queryset.first()

        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfgen import canvas
        except Exception:
            self.message_user(
                request,
                "Le module PDF n'est pas disponible (reportlab).",
                level=messages.ERROR,
            )
            return

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        margin_x = 18 * mm
        y = height - 18 * mm

        # Logo
        logo_path = settings.BASE_DIR / 'reservations' / 'static' / 'reservations' / 'logo.png'
        if logo_path.exists():
            try:
                c.drawImage(ImageReader(str(logo_path)), margin_x, y - 18 * mm, width=35 * mm, height=18 * mm, mask='auto')
            except Exception:
                pass

        # En-tête
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin_x + 42 * mm, y - 8 * mm, "DEVIS")

        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 42 * mm, y - 14 * mm, f"Date : {timezone.localdate().strftime('%d/%m/%Y')}")
        c.drawString(margin_x + 42 * mm, y - 20 * mm, f"Référence : DEM-{demande.id}")

        y -= 34 * mm

        # Client
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Client")
        y -= 6 * mm

        c.setFont("Helvetica", 10)
        c.drawString(margin_x, y, f"Nom : {demande.nom}")
        y -= 5 * mm
        c.drawString(margin_x, y, f"Email : {demande.email}")
        y -= 5 * mm
        c.drawString(margin_x, y, f"Téléphone : {demande.numero_telephone}")
        y -= 8 * mm

        # Adresse
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Adresse d'intervention")
        y -= 6 * mm

        c.setFont("Helvetica", 10)
        c.drawString(margin_x, y, f"{demande.rue}")
        y -= 5 * mm
        c.drawString(margin_x, y, f"{demande.code_postal} {demande.ville}")
        y -= 8 * mm

        # Détails prestation
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Détails")
        y -= 6 * mm

        c.setFont("Helvetica", 10)
        c.drawString(margin_x, y, f"Type : {demande.get_type_prestation_display()}")
        y -= 5 * mm
        c.drawString(margin_x, y, f"Surface : {demande.surface} m²")
        y -= 5 * mm

        date_souhaitee = demande.date_souhaitee.strftime('%d/%m/%Y') if demande.date_souhaitee else "Non précisée"
        c.drawString(margin_x, y, f"Date souhaitée : {date_souhaitee}")
        y -= 5 * mm

        materiel = "Oui" if demande.materiel_sur_place else "Non"
        c.drawString(margin_x, y, f"Matériel sur place : {materiel}")
        y -= 8 * mm

        # Prix
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Prix")
        y -= 6 * mm

        c.setFont("Helvetica", 10)
        prix_txt = f"{demande.prix_devis} €" if demande.prix_devis is not None else "Non renseigné"
        c.drawString(margin_x, y, f"Prix du devis : {prix_txt}")
        y -= 10 * mm

        # Notes
        c.setFont("Helvetica", 9)
        c.drawString(margin_x, y, "Ce devis est fourni à titre indicatif et peut être ajusté après confirmation des détails.")

        c.showPage()
        c.save()

        buffer.seek(0)
        filename = f"devis-dem-{demande.id}-{slugify(demande.nom) or 'client'}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    generer_devis_pdf.short_description = "Générer un devis (PDF)"

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
class DemandeAccepteeAdmin(DemandeNettoyageAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(statut='ACCEPTEE')


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('nom_client', 'note', 'publie', 'date_creation')
    list_filter = ('note', 'publie', 'type_prestation')
    search_fields = ('nom_client', 'texte')
    readonly_fields = ('date_creation',)
    actions = ['delete_selected']
    
    fieldsets = (
        ('Client', {
            'fields': ('nom_client',)
        }),
        ('Avis', {
            'fields': ('note', 'texte', 'type_prestation')
        }),
        ('Gestion', {
            'fields': ('publie', 'date_creation')
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_prestation', 'affichee', 'date_creation')
    list_filter = ('type_prestation', 'affichee')
    search_fields = ('titre', 'description')
    readonly_fields = ('date_creation', 'apercu_image')
    actions = ['delete_selected']
    
    fieldsets = (
        ('Photo', {
            'fields': ('titre', 'image', 'apercu_image', 'description')
        }),
        ('Type', {
            'fields': ('type_prestation',)
        }),
        ('Gestion', {
            'fields': ('affichee', 'date_creation')
        }),
    )
    
    def apercu_image(self, obj):
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-width: 300px;" />', obj.image.url)
        return "-"
    apercu_image.short_description = "Aperçu" 
