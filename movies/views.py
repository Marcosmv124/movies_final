from django.shortcuts import render
from django.http import HttpResponse
from movies.models import Movie, MovieReview
from django.shortcuts import get_object_or_404, redirect


# =========================
# HOME / LISTADO
# =========================
def index(request):
    movies = Movie.objects.all().order_by('title')  # 👈 ORDEN A–Z
    context = {
        'movies': movies,
        'message': 'welcome'
    }
    return render(request, 'movies/index.html', context)


# =========================
# DETALLE DE PELÍCULA
# =========================
def movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    user_has_liked = (
        movie.likes.filter(id=request.user.id).exists()
        if request.user.is_authenticated else False
    )

    context = {
        'movie': movie,
        'saludo': 'welcome',
        'user_has_liked': user_has_liked
    }
    return render(request, 'movies/movie.html', context)


# =========================
# REVIEWS (HTMX)
# =========================
def movie_reviews(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/reviews.html', {'movie': movie})


def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        review = request.POST.get('review')

        MovieReview.objects.create(
            movie=movie,
            rating=rating,
            title=title,
            review=review,
            user=request.user
        )

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})

    return render(request, 'movies/movie_review_form.html', {'movie': movie})


# =========================
# BUSCADOR
# =========================
def movie_search(request):
    search_query = request.GET.get('search', '')

    if search_query:
        movies = Movie.objects.filter(
            title__icontains=search_query
        ).order_by('title')
    else:
        movies = Movie.objects.all().order_by('title')

    return render(
        request,
        'movies/search_results.html',
        {
            'movies': movies,
            'search_value': search_query
        }
    )


# =========================
# LIKE / UNLIKE
# =========================
def toggle_like(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if movie.likes.filter(id=request.user.id).exists():
        movie.likes.remove(request.user)
    else:
        movie.likes.add(request.user)

    return redirect('movie_detail', movie_id=movie.id)


# =========================
# FAVORITOS
# =========================
def favorite_movies(request):
    favorite_movies = Movie.objects.filter(likes=request.user).order_by('title')
    context = {
        'favorite_movies': favorite_movies
    }
    return render(request, 'movies/favorite_movies.html', context)
