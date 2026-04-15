from django.db import models

from django.db import models

class DemandeNettoyage(models.Model):
    # --- Client ---
    nom = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse email") # Nouveau !
    numero_telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")

    # --- Prestation ---
    TYPE_PRESTATION_CHOICES = [('AIRBNB', 'AirBnb'), ('BUREAU', 'Bureau'), ('MAISON', 'Maison / Appartement')]
    type_prestation = models.CharField(max_length=20, choices=TYPE_PRESTATION_CHOICES, verbose_name="Type de prestation")
    surface = models.IntegerField(verbose_name="Surface (en m²)") # Nouveau !

    # --- Adresse détaillée ---
    rue = models.CharField(max_length=255, verbose_name="Numéro et nom de rue")
    code_postal = models.CharField(max_length=5, verbose_name="Code postal (5 chiffres)")
    ville = models.CharField(max_length=100, verbose_name="Ville")

    # --- Détails techniques ---
    nombre_chambres = models.IntegerField(default=0, verbose_name="Nombre de chambres")
    nombre_salons = models.IntegerField(default=0, verbose_name="Nombre de salons")
    nombre_bureaux = models.IntegerField(default=0, verbose_name="Nombre de bureaux") # Nouveau !
    nombre_toilettes = models.IntegerField(default=1, verbose_name="Nombre de toilettes/SdB")
    materiel_sur_place = models.BooleanField(default=False, verbose_name="Matériel fourni sur place")

    # --- Gestion ---
    STATUT_CHOICES = [('ATTENTE', 'En attente'), ('ACCEPTEE', 'Acceptée'), ('REFUSEE', 'Refusée')]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ATTENTE')
    commentaire_admin = models.TextField(blank=True, null=True, verbose_name="Message au client (MyCleaning)")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.ville} ({self.surface}m²)"
    # À la fin de ton fichier models.py

class DemandeAcceptee(DemandeNettoyage):
    class Meta:
        proxy = True # C'est le mot magique : Django ne créera pas de nouvelle table
        verbose_name = "Demande Acceptée"
        verbose_name_plural = "✅ Demandes Acceptées" # Un petit emoji pour que ta mère le repère vite !


class Avis(models.Model):
    """Modèle pour les avis clients"""
    nom_client = models.CharField(max_length=100, verbose_name="Nom du client")
    note = models.IntegerField(choices=[(5, '⭐⭐⭐⭐⭐ 5 stars'), (4, '⭐⭐⭐⭐ 4 stars'), (3, '⭐⭐⭐ 3 stars'), (2, '⭐⭐ 2 stars'), (1, '⭐ 1 star')], verbose_name="Note")
    texte = models.TextField(verbose_name="Avis")
    type_prestation = models.CharField(max_length=20, choices=[('AIRBNB', 'AirBnb'), ('BUREAU', 'Bureau'), ('MAISON', 'Maison / Appartement'), ('AUTRE', 'Autre')], default='AUTRE', verbose_name="Type de prestation")
    publie = models.BooleanField(default=True, verbose_name="Publié")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom_client} - {self.note} ⭐"


class Photo(models.Model):
    """Modèle pour les photos de nettoyage"""
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='photos_nettoyage/', verbose_name="Image")
    type_prestation = models.CharField(max_length=20, choices=[('AIRBNB', 'AirBnb'), ('BUREAU', 'Bureau'), ('MAISON', 'Maison / Appartement'), ('AUTRE', 'Autre')], default='AUTRE', verbose_name="Type de prestation")
    affichee = models.BooleanField(default=True, verbose_name="Affichée sur l'accueil")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre
