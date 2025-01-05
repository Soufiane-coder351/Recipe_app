from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from recipes.models import Recipe, Avis, Ingredient, Produit, Favorites, Step
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.utils import IntegrityError

# Vue d'accueil qui affiche la liste de toutes les recettes avec pagination
def index(request):
    template = loader.get_template("./recipes/index.html")
    liste_recettes = Recipe.objects.all()
    paginator = Paginator(liste_recettes, 8)  # 8 recettes par page
    page_number = request.GET.get('page')  # Numéro de la page actuelle
    recettes = paginator.get_page(page_number)  # Obtenez les recettes pour la page

    return HttpResponse(template.render(request=request, context={"recettes": recettes}))


# Vue pour créer une nouvelle recette
@login_required
def createrecipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        user = request.user
        errors = []

        # Obtenez les ingrédients depuis la requête
        ingredients = request.POST.get('ingredients')  # Chaîne de caractères séparée par des virgules
        
        # Obtenez dynamiquement les étapes de la recette
        steps = []
        step_count = 1
        while f'stepDescription{step_count}' in request.POST:
            step_description = request.POST.get(f'stepDescription{step_count}')
            step_image = request.FILES.get(f'stepImage{step_count}')
            if step_description:
                steps.append({
                    'description': step_description,
                    'image': step_image,
                    'order': step_count,  # Définir l'ordre des étapes en fonction du compteur
                })
            step_count += 1

        # Vérifier si une recette avec ce titre existe déjà
        if Recipe.objects.filter(title=title).exists():
            errors.append("Titre de la recette existe déjà")

        if not errors:
            try:
                # Créer la recette
                recipe = Recipe.objects.create(title=title, description=description, user=user, image=image)
                recipe.save()

                # Convertir la chaîne d'ingrédients en une liste
                ingredient_list = ingredients.split(',') if ingredients else []

                # Créer les ingrédients pour la recette
                for ingredient_name in ingredient_list:
                    if ingredient_name:
                        produit, created = Produit.objects.get_or_create(name=ingredient_name)
                        Ingredient.objects.create(produit=produit, recette=recipe, qtté="")  # Quantité par défaut vide

                # Créer les étapes pour la recette
                for step_data in steps:
                    Step.objects.create(
                        recipe=recipe,
                        description=step_data['description'],
                        image=step_data['image'],
                        order=step_data['order'],
                    )

                return redirect('profile')

            except Exception as e:
                errors.append(str(e))

        return render(request, 'recipes/createrecipe.html', {'errors': errors, 'values': {
            'title': title,
            'description': description,
            'steps': steps,
        }})

    return render(request, "recipes/createrecipe.html")


# Vue pour afficher les détails d'une recette
def recette_info(request, recipe_id):
    try:
        recette = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return HttpResponse("Recipe not found", status=404)
    
    is_favorited = Favorites.objects.filter(user=request.user, recette=recette).exists() if request.user.is_authenticated else False
    reviews = Avis.objects.filter(recipe=recette)
    ingredients = Ingredient.objects.filter(recette=recette)
    steps = Step.objects.filter(recipe=recette)
    return render(request, 'recipes/recette_info.html', {'recette': recette, 'is_favorited': is_favorited, 'reviews': reviews, 'ingredients': ingredients, 'steps': steps})


# Vue pour afficher les recettes favorites de l'utilisateur
@login_required
def afficher_favoris(request):
    favoris = Favorites.objects.filter(user=request.user)
    return render(request, 'recipes/favorites.html', {"favoris": favoris})


# Vue pour rechercher des recettes par titre
def chercher_recette(request):
    q = request.GET.get('query', '')  # Obtenir le mot-clé de recherche depuis l'URL
    recherches = Recipe.objects.filter(title__icontains=q)  # Rechercher dans le champ "title"
    return render(request, "recipes/search_result.html", {'recherches': recherches})


# Vue pour ajouter ou retirer une recette des favoris
def toggle_favorite(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return HttpResponse("Recipe not found", status=404)
    
    favorite = Favorites.objects.filter(user=request.user, recette=recipe).first()

    if favorite:
        # Si la recette est déjà dans les favoris, on la supprime
        favorite.delete()
    else:
        # Sinon, on l'ajoute aux favoris
        Favorites.objects.create(user=request.user, recette=recipe)
    
    # Rediriger vers la page des détails de la recette
    return redirect('recette_info', recipe_id=recipe.id)


# Vue pour soumettre un avis sur une recette
@login_required
def submit_review(request):
    if request.method == "POST":
        recipe_id = request.POST.get('recipe_id')
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return HttpResponse("Recipe not found", status=404)
        
        try:
            rating = request.POST.get('rating')            
            comment = request.POST.get('comment')  
            # Sauvegarder la note et le commentaire dans la base de données
            Avis.objects.create(recipe=recipe, user=request.user, content=comment, rating=rating)
            messages.success(request, "Votre avis est transmis avec succès !")
        except IntegrityError as e:
            messages.error(request, "Vous devez mettre une note")
        
        return redirect('recette_info', recipe_id=recipe.id)  # Rediriger vers la page de la recette
    return HttpResponse("Invalid request method.", status=405)


# Vue pour supprimer un avis
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Avis, id=review_id)

    # Vérifier que l'utilisateur est le propriétaire du commentaire
    if review.user != request.user:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce commentaire.")
        return redirect('recette_info', recipe_id=review.recipe.id)
    
    review.delete()
    messages.success(request, "Votre commentaire a été supprimé avec succès.")
    return redirect('recette_info', recipe_id=review.recipe.id)
