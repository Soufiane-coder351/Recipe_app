from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from recipes.models import Recipe, Favorites
from django.contrib import messages


# Create your tests here.
class LoginViewTests(TestCase):
    def setUp(self):
        """Préparation de l'utilisateur pour les tests."""
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.url = reverse('login')  # l'URL de la vue de login
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        self.invalid_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }

    def test_login_with_valid_credentials(self):
        """Vérifie que l'utilisateur se connecte avec des informations valides."""
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse('profile'))  # Ajustez selon votre page de redirection après la connexion
        # Vérifie que l'utilisateur est bien connecté
        self.assertEqual(str(response.wsgi_request.user), 'testuser')

    def test_login_with_invalid_credentials(self):
        """Vérifie que l'authentification échoue avec des informations invalides."""
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, 200)
        # Vérifie que le message d'erreur est affiché
        self.assertContains(response, "mot de passe invalide")


class SignupViewTests(TestCase):
    
    def setUp(self):
        """Configuration des données nécessaires pour les tests"""
        self.url = reverse('signup')  # Remplacez 'signup' par le nom réel de votre URL de signup
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        self.invalid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'short',
            'confirm_password': 'short'
        }

    def test_signup_successful(self):
        """Test si l'inscription de l'utilisateur réussit"""
        response = self.client.post(self.url, self.valid_data)
        # Vérifie si l'utilisateur a été redirigé après l'inscription
        self.assertRedirects(response, reverse('profile'))  # Remplacez 'profile' par l'URL de votre page de profil
        # Vérifie si l'utilisateur a bien été créé dans la base de données
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('password123'))  # Vérifie si le mot de passe est correctement haché

    def test_signup_page_renders_correctly(self):
        """Test si la page d'inscription se charge correctement"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')

    
class ProfileViewTests(TestCase):
    
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        
        # Créer quelques recettes de test pour l'utilisateur
        self.recipe_1 = Recipe.objects.create(title="Recipe 1", description="Test description", user=self.user)
        self.recipe_2 = Recipe.objects.create(title="Recipe 2", description="Test description", user=self.user)
        
        # Créer des favoris pour l'utilisateur
        self.favorite_1 = Favorites.objects.create(user=self.user, recette=self.recipe_1)
        self.favorite_2 = Favorites.objects.create(user=self.user, recette=self.recipe_2)
        
        # Connecter l'utilisateur de test
        self.client.login(username='testuser', password='password123')
        
        # Définir l'URL de la vue du profil (ajustez le nom si nécessaire)
        self.url = reverse('profile')

    def test_profile_view_context_data(self):
        """Tester si les bonnes données de contexte sont passées au template."""
        response = self.client.get(self.url)
        
        # Vérifier si les variables de contexte 'recettes_user' et 'recettesfav' contiennent les données attendues
        self.assertEqual(len(response.context['recettes_user']), 2)  # Deux recettes créées pour l'utilisateur
        self.assertEqual(len(response.context['recettesfav']), 2)  # Deux favoris créés pour l'utilisateur

    def test_profile_view_no_favorites(self):
        """Tester la vue du profil lorsque l'utilisateur n'a pas de favoris."""
        # Se connecter avec un autre utilisateur qui n'a pas de favoris
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='password123')
        self.client.login(username='newuser', password='password123')
        
        response = self.client.get(self.url)
        
        # Vérifier que la variable de contexte 'recettesfav' est vide (pas de favoris)
        self.assertEqual(len(response.context['recettesfav']), 0)


class DeleteRecipeTests(TestCase):
    def setUp(self):
        """Configurer les données nécessaires pour les tests"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        
        # Créer une recette liée à l'utilisateur
        self.recipe = Recipe.objects.create(title="Test Recipe", description="Test description", user=self.user)

        # Connecter l'utilisateur
        self.client.login(username='testuser', password='password123')

        # URL pour supprimer la recette
        self.url = reverse('delete_recipe', kwargs={'recette_id': self.recipe.id})

    def test_delete_recipe_status_code(self):
        """Tester si la suppression de la recette retourne un code de statut 302 (redirection)."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirection après suppression

    def test_recipe_deleted_from_database(self):
        """Tester si la recette est bien supprimée de la base de données après l'appel de la vue."""
        self.client.post(self.url)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())  # Vérifier si la recette n'existe plus