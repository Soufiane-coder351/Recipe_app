from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from recipes.models import Recipe, Favorites
from django.contrib import messages
from django.shortcuts import get_object_or_404


# Vue pour la connexion de l'utilisateur
def login_view(request):
    if request.method == 'POST':
        # Récupération des données du formulaire depuis la requête POST
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Initialisation d'une liste vide pour les erreurs
        errors = []
        # Authentifier l'utilisateur avec l'email (au lieu du nom d'utilisateur)
        try:
            # Trouver l'utilisateur par email
            user = User.objects.get(email=email)
            
            # Authentifier avec le mot de passe
            if user.check_password(password):
                user = authenticate(request, username=user.username, password=password)
            else:
                user = None
        except User.DoesNotExist:
            user = None

        # Si l'authentification échoue, afficher une erreur
        if user is None:
            errors.append("Nom d'utilisateur ou mot de passe invalide.")
        else:
            # Si l'authentification est réussie, connecter l'utilisateur
            login(request, user)
            # Rediriger vers la page de profil ou la page d'accueil après la connexion réussie
            return redirect('profile')  # Ajustez selon la page cible après la connexion

        # Si des erreurs existent, afficher la page de connexion avec les messages d'erreur
        return render(request, 'user/login.html', {'errors': errors})
    return render(request, 'user/login.html')    


# Vue pour l'inscription de l'utilisateur
def signup_view(request):
    if request.method == 'POST':
        # Récupération des données du formulaire depuis la requête POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Initialisation d'une liste vide pour les erreurs
        errors = []

        # Validation des données du formulaire manuellement
        if password != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")
        
        if len(password) < 8:  # Vous pouvez ajouter d'autres vérifications ici
            errors.append("Le mot de passe doit comporter au moins 8 caractères.")
        
        # Vérification si le nom d'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            errors.append("Le nom d'utilisateur est déjà pris.")

        # Vérification si l'email existe déjà
        if User.objects.filter(email=email).exists():
            errors.append("L'email est déjà pris.")
        
        # Si aucune erreur, création de l'utilisateur
        if not errors:
            try:
                # Création de l'utilisateur
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Connexion de l'utilisateur après la création
                login(request, user)

                # Redirection vers la page de profil ou d'accueil après l'inscription réussie
                return redirect('profile')  # Assurez-vous d'avoir une page 'profile' ou toute autre page

            except Exception as e:
                errors.append(str(e))

        # Si des erreurs existent, afficher la page d'inscription avec les messages d'erreur
        return render(request, 'user/signup.html', {'errors': errors})

    else:
        # Initialisation du formulaire de création d'utilisateur (si la méthode n'est pas POST)
        form = UserCreationForm()

    return render(request, 'user/signup.html', {'form': form})


# Vue pour afficher le profil de l'utilisateur connecté
@login_required
def profile_view(request):
    # Récupérer les recettes de l'utilisateur et celles qu'il a ajoutées aux favoris
    recettes_user = Recipe.objects.filter(user=request.user)
    recettesfav = Favorites.objects.filter(user=request.user)
    return render(request, 'user/profile.html', {'recettes_user': recettes_user, 'recettesfav': recettesfav})


# Vue pour changer le mot de passe de l'utilisateur
@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Initialisation d'une liste vide pour les erreurs
        errors = []

        # Vérification si l'ancien mot de passe est correct
        if not request.user.check_password(old_password):
            errors.append("Le mot de passe actuel est incorrect.")

        # Validation que les nouveaux mots de passe correspondent
        if new_password1 != new_password2:
            errors.append("Les nouveaux mots de passe ne correspondent pas.")

        # Validation de la longueur du nouveau mot de passe
        if len(new_password1) < 8:
            errors.append("Le nouveau mot de passe doit comporter au moins 8 caractères.")

        # Si aucune erreur, mise à jour du mot de passe
        if not errors:
            try:
                # Sauvegarder le nouveau mot de passe
                request.user.set_password(new_password1)
                request.user.save()

                # Garder l'utilisateur connecté après le changement de mot de passe
                update_session_auth_hash(request, request.user)

                return redirect('profile')  # Redirection vers la page de profil après succès
            except Exception as e:
                errors.append(str(e))

        # Si des erreurs existent, afficher le formulaire à nouveau avec les erreurs
        return render(request, 'user/change_password.html', {'errors': errors})
    return render(request, 'user/change_password.html')


# Vue pour déconnecter l'utilisateur
@login_required
def logout_view(request):
    logout(request)  # Déconnecter l'utilisateur
    return redirect('recipes')  # Rediriger vers la page des recettes


# Vue pour changer le nom de l'utilisateur
@login_required
def change_name(request):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')

        # Mise à jour du nom d'utilisateur
        request.user.username = new_name
        request.user.save()

        return redirect('profile')  # Redirection après succès

    # Rendre le template pour la requête GET
    return render(request, 'user/change_name.html')


# Vue pour supprimer une recette de l'utilisateur
@login_required
def delete_recipe(request, recette_id):
    recette = get_object_or_404(Recipe, id=recette_id, user=request.user)
    recette.delete()
    return redirect('profile')  # Redirigez vers la page du profil
