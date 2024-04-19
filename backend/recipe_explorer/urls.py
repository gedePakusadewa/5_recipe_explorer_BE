from django.urls import path
from recipe_explorer.views import LogIn, SignUp, LogOut, RecipeExplorer, Profile, Favorite, RecipeDetail

urlpatterns= [
    path('login', LogIn.as_view()),
    path('signup', SignUp.as_view()),
    path('logout', LogOut.as_view()),
    path('', RecipeExplorer.as_view()),
    path('profile', Profile.as_view()),
    path('favorite', Favorite.as_view()),
    path('recipe-detail', RecipeDetail.as_view()),
]