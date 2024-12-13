from django.shortcuts import render
from django.http import HttpResponse
from movies.models import Movie, MovieReview
#from movies.forms import MovieReviewForm
#from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect



# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = { 'movies':movies, 'message':'welcome' }
    return render(request,'movies/index.html', context=context )
    
# En la vista movie
def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
   # review_form = MovieReviewForm()
    # Verificar si el usuario autenticado ya ha dado "me gusta"
    user_has_liked = movie.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    context = { 
        'movie': movie, 
        'saludo': 'welcome', 
      #  'review_form': review_form, 
        'user_has_liked': user_has_liked  # Pasar el estado del "me gusta"
    }
    return render(request, 'movies/movie.html', context=context)

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )

def add_review(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    #Verifico que el usuario alla enviado datos
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        review = request.POST.get('review')
        movie_review = MovieReview(
            movie=movie,
            rating=rating,
            title=title,
            review=review,
            user=request.user
        )
        movie_review.save()
        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    return render(request, 'movies/movie_review_form.html', {'movie': movie})



#Busqueda
def movie_search(request):
    search_query = request.GET.get('search', '')  # Obtén el término de búsqueda
    if search_query:
        # Filtrar las películas que contengan el término de búsqueda en el título
        movies = Movie.objects.filter(title__icontains=search_query)
    else:
        # Si no hay término de búsqueda, mostrar todas las películas
        movies = Movie.objects.all()
    
    return render(request, 'movies/search_results.html', {'movies': movies, 'search_value': search_query})

#@login_required
def toggle_like(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.likes.filter(id=request.user.id).exists():
        movie.likes.remove(request.user)  # Quitar "me gusta"
    else:
        movie.likes.add(request.user)  # Dar "me gusta"
    
    # Redirigir correctamente a la vista de detalle de la película
    return redirect('movie_detail', movie_id=movie.id)  # 

#@login_required
def favorite_movies(request):
    # Obtener todas las películas que el usuario ha marcado como favoritas (con "me gusta")
    favorite_movies = Movie.objects.filter(likes=request.user)
    context = {'favorite_movies': favorite_movies}
    return render(request, 'movies/favorite_movies.html', context)