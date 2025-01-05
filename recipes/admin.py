from django.contrib import admin
from .models import Produit
from .models import Recipe
from .models import Avis
from .models import Ingredient

# Register your models here.


admin.site.register(Produit)
admin.site.register(Recipe)
admin.site.register(Avis)
admin.site.register(Ingredient)
