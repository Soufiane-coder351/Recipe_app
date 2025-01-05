import recipes.views 
from django.urls import path


urlpatterns=[
    path('',recipes.views.index,name='recipes'),
    path('createrecipe',recipes.views.createrecipe, name="createrecipe"),
    path('favoris/',recipes.views.afficher_favoris, name="recettes_favorites"),
    path('<int:recipe_id>',recipes.views.recette_info, name="recette_info"),
    path('chercher_recette/', recipes.views.chercher_recette, name='chercher_recette'),
    path('recette/<int:recipe_id>/favorite/', recipes.views.toggle_favorite, name='toggle_favorite'),
    path('submit_review/', recipes.views.submit_review, name='submit_review'),
    path('review/delete/<int:review_id>/', recipes.views.delete_review, name='delete_review'),
    
]