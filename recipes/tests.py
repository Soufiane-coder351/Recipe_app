from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from recipes.models import Recipe, Produit, Ingredient, Step, Avis, Favorites
from recipes.views import index
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
# Create your tests here.
class IndexViewTests(TestCase):
    def setUp(self):
        # Initialiser une instance de RequestFactory pour simuler les requêtes
        self.factory = RequestFactory()
        self.url = reverse('recipes') 
    
    def test_vue_charge_correctement(self):
        """Tester si la vue index se charge correctement."""
        request = self.factory.get(self.url)
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_template_utilise(self):
        """Tester si le bon template est utilisé."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, './recipes/index.html')

    def test_pagination(self):
        """Tester si la pagination fonctionne correctement."""
        response = self.client.get(self.url)
        self.assertTrue(len(response.context['recettes']) <= 8)  # 8 recettes par page par défaut


class CreateRecipeTests(TestCase):
    def setUp(self):
        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = Client()
        self.client.login(username="testuser", password="password123")  # Connexion automatique pour les tests
        self.url = reverse('createrecipe') 

    def test_creation_recette_succes(self):
        """Tester la création d'une recette avec succès."""
        # Préparer les données POST
        data = {
            'title': 'Test Recipe',
            'description': 'This is a test recipe',
            'ingredients': 'Tomato,Cheese,Basil',
            'stepDescription1': 'Chop the tomatoes',
            'stepDescription2': 'Add cheese and basil',
        }
        files = {
            'image': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        }

        response = self.client.post(self.url, data=data, files=files)

        # Vérifier la redirection après succès
        self.assertRedirects(response, reverse('profile'))

        # Vérifier que la recette a été créée
        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.title, 'Test Recipe')

        # Vérifier les ingrédients
        self.assertEqual(Ingredient.objects.count(), 3)
        self.assertTrue(Produit.objects.filter(name='Tomato').exists())

        # Vérifier les étapes
        self.assertEqual(Step.objects.count(), 2)
        self.assertEqual(Step.objects.first().description, 'Chop the tomatoes')


class RecetteInfoTests(TestCase):
    def setUp(self):
        # Créer un utilisateur pour simuler une connexion
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Créer une recette
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            description="Test description",
            user=self.user,
        )
        
        # Ajouter des ingrédients à la recette
        self.ingredient1 = Produit.objects.create(name="Tomate")
        self.ingredient2 = Produit.objects.create(name="Fromage")
        
        Ingredient.objects.create(produit=self.ingredient1, recette=self.recipe, qtté="2 tomates")
        Ingredient.objects.create(produit=self.ingredient2, recette=self.recipe, qtté="100g de fromage")
        
        # Ajouter des étapes à la recette
        self.step1 = Step.objects.create(recipe=self.recipe,description="Étape 1 description",order=1)
        self.step2 = Step.objects.create(recipe=self.recipe,description="Étape 2 description",order=2)
        
        # Ajouter un avis à la recette
        self.avis = Avis.objects.create(user=self.user,recipe=self.recipe,content="C'est une excellente recette !",rating=5)
        
        # Ajouter la recette aux favoris pour l'utilisateur
        self.favorite = Favorites.objects.create(user=self.user,recette=self.recipe)
        
        # Définir l'URL de la recette
        self.url = reverse('recette_info', args=[self.recipe.id])

    def test_recette_info_context_data(self):
        """Vérifie que la vue transmet les bonnes données au contexte."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['recette'], self.recipe)
        self.assertTrue('is_favorited' in response.context)
        self.assertEqual(len(response.context['reviews']), 1)  # Un avis dans notre test
        self.assertEqual(len(response.context['ingredients']), 2)  # Deux ingrédients
        self.assertEqual(len(response.context['steps']), 2)  # Deux étapes
    
    def test_is_favorited_authenticated_user(self):
        """Vérifie que l'utilisateur authentifié voit la recette comme favorite."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        # Vérifier que le favori est bien marqué comme True dans le contexte
        self.assertTrue(response.context['is_favorited'])


class AfficherFavorisTests(TestCase):
    def setUp(self):
        # Création d'un utilisateur pour l'exécution des tests
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Création de recettes
        self.recipe1 = Recipe.objects.create(title='Recipe 1', description='Test description 1', user=self.user)
        self.recipe2 = Recipe.objects.create(title='Recipe 2', description='Test description 2', user=self.user)

        # Création de favoris
        self.favorite1 = Favorites.objects.create(user=self.user, recette=self.recipe1)
        self.favorite2 = Favorites.objects.create(user=self.user, recette=self.recipe2)

        # URL de la vue
        self.url = reverse('recettes_favorites')

    def test_favoris_displayed(self):
        """Vérifie que les favoris de l'utilisateur sont affichés correctement."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        # Vérifie que les titres des recettes favorisées sont présents dans la réponse
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, self.recipe2.title)


class ChercherRecetteTests(TestCase):

    def setUp(self):
        """Configurer les données nécessaires pour les tests"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        
        # Créer quelques recettes liées à l'utilisateur
        self.recipe1 = Recipe.objects.create(title="Recette Test 1", description="Description 1", user=self.user)
        self.recipe2 = Recipe.objects.create(title="Recette Test 2", description="Description 2", user=self.user)
        self.recipe3 = Recipe.objects.create(title="Autre Recette", description="Description 3", user=self.user)

    def test_search_by_title(self):
        """Tester si la recherche par titre fonctionne correctement"""
        response = self.client.get(reverse('chercher_recette'), {'query': 'Test'})
        # Vérifier que les recettes contenant "Test" dans le titre sont retournées
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, self.recipe2.title)
        self.assertNotContains(response, self.recipe3.title)

    def test_search_case_insensitive(self):
        """Tester si la recherche est insensible à la casse"""
        response = self.client.get(reverse('chercher_recette'), {'query': 'test'})
        # Vérifier que la recherche est insensible à la casse et retourne les recettes appropriées
        self.assertContains(response, self.recipe1.title)
        self.assertContains(response, self.recipe2.title)