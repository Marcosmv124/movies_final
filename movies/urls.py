from django.urls import path
from .views import *

urlpatterns = [
   path('<int:movie_id>/', movie, name='movie_detail'),
   path('<int:movie_id>/', movie),
   path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('', index), 
    path('search', movie_search, name='search_results'),  # No incluyas la barra final
    #path('favorite/manage/', name='manage_favorites'),
    path('toggle_like/<int:movie_id>/', toggle_like, name='toggle_like'),
     path('favorite_movies', favorite_movies, name='favorite_movies'),
]
