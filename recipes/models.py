from django.db import models
from django.contrib.auth.models import User

# Création du modèle pour l'ingrédient
class Produit(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Le modèle pour l'utilisateur est déjà fourni par Django, on peut l'importer avec : from django.contrib.auth.models import User

# Modèle pour la recette (Recipe)
class Recipe(models.Model):
    title = models.CharField(max_length=200)  # Titre de la recette
    description = models.TextField()  # Description détaillée de la recette
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Utilisateur ayant créé la recette
    image = models.ImageField(upload_to='recipes_photos/', default="https://dummyimage.com/450x300/dee2e6/6c757d.jpg")  # Image de la recette

    def __str__(self):
        return self.title
    

# Modèle pour l'étape de la recette (Step), liée à Recipe
class Step(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='steps', on_delete=models.CASCADE)  # La recette à laquelle cette étape appartient
    description = models.TextField()  # Description de l'étape
    image = models.ImageField(upload_to='step_images/', blank=True, null=True)  # Image optionnelle pour chaque étape
    order = models.PositiveIntegerField()  # L'ordre de l'étape dans la recette

    class Meta:
        ordering = ['order']  # Assure que les étapes sont ordonnées selon le champ 'order'

    def __str__(self):
        return f"Étape {self.order} pour {self.recipe.title}"

# Relation ManyToMany entre Recipe et User pour les avis (Avis)
class Avis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Utilisateur ayant écrit l'avis
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)  # Recette à laquelle cet avis se rapporte
    content = models.TextField()  # Contenu de l'avis
    rating = models.PositiveIntegerField(default=0)  # Note (optionnelle) de l'avis
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp de la création de l'avis

    def __str__(self):
        return f'Avis de {self.user.username} sur {self.recipe.title}'

# Modèle pour les ingrédients dans une recette
class Ingredient(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)  # Référence au produit (ingrédient)
    recette = models.ForeignKey(Recipe, on_delete=models.CASCADE)  # Référence à la recette à laquelle l'ingrédient appartient
    qtté = models.TextField()  # Quantité de l'ingrédient utilisée dans la recette

# Modèle pour les favoris d'un utilisateur
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Utilisateur qui a ajouté cette recette aux favoris
    recette = models.ForeignKey(Recipe, on_delete=models.CASCADE)  # Recette ajoutée aux favoris
