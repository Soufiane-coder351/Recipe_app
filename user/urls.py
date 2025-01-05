import user.views
from django.urls import re_path,path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/',user.views.login_view, name='login'),
    path('signup/',user.views.signup_view , name='signup'),
    path('profile/',user.views.profile_view, name="profile"),
    path('logout/', user.views.logout_view, name='logout'),
    path('change-password/', user.views.change_password, name='change_password'),
    path('change-name/', user.views.change_name, name='change_name'),
    path('profile/delete_recipe/<int:recette_id>/', user.views.delete_recipe, name='delete_recipe'),

]
