from typing import Any
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import FormView, TemplateView, ListView
from django.views.decorators.http import require_http_methods

from films.forms import RegisterForm
from films.models import Film, UserFilms
from films.utils import get_order_for_new_film, reorder_films_after_delete


class IndexView(TemplateView):
    template_name = "index.html"


class Login(LoginView):
    template_name = "registration/login.html"


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


def check_username(request):
    username = request.POST.get("username")
    
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div id='username-error' class='error'>This username already exists</div>") # with hx-swap="outerhtml"
        # return HttpResponse("This username already exists!")
    else:
        return HttpResponse("<div id='username-error' class='success'>This username is available</div>") # with hx-swap="outerhtml"
    

class FilmListView(LoginRequiredMixin, ListView):
    template_name = "films.html"
    model = Film
    context_object_name = "user_films"
    paginate_by = 2

    def get_queryset(self) -> QuerySet[Any]:
        return UserFilms.objects.filter(user=self.request.user)

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return "partials/film-list-elements.html"
        return "films.html"    


@login_required
def add_film(request):
    user = request.user
    filmname = request.POST.get("filmname")

    film = Film.objects.get_or_create(name=filmname)[0]

    if not UserFilms.objects.filter(film=film, user=user).exists():
        UserFilms.objects.create(film=film, user=user, order=get_order_for_new_film(user)) # add order to the new film

    messages.success(request, f"Added <em><b>{filmname}</b></em> to your list of films.")

    user_films = UserFilms.objects.filter(user=user)

    return render(request, "partials/film-list.html", {"user_films": user_films})


@login_required
@require_http_methods(["DELETE"])
def remove_film(request, pk):
    user = request.user

    UserFilms.objects.filter(pk=pk).delete()

    user_films = reorder_films_after_delete(user)

    return render(request, "partials/film-list.html", {"user_films": user_films})


@login_required
def search_film(request):
    search_text = request.POST.get("search")
    user_film_names = UserFilms.objects.filter(user=request.user).values_list("film__name", flat=True)
    results = Film.objects.filter(name__icontains=search_text).exclude(name__in=user_film_names)

    return render(request, "partials/search-results.html", {"results": results})
    

def message_clear(request):
    return HttpResponse("")


@login_required
def sort_films(request):
    film_pks_order = request.POST.getlist("film_order")
    films = []

    for index, film_pk in enumerate(film_pks_order, start=1):
        user_film = UserFilms.objects.get(pk=film_pk)
        user_film.order = index
        user_film.save(update_fields=["order"])
        films.append(user_film)

    return render(request, "partials/film-list.html", {"user_films": user_films})


@login_required
def detail_film(request, pk):
    print("detail_film", pk)
    user_film = get_object_or_404(UserFilms, pk=pk)

    return render(request, "partials/film-detail.html", {"user_film": user_film})


@login_required
def film_list_partial(request):
    user_films =  UserFilms.objects.filter(user=request.user)
    return render(request, "partials/film-list.html", {"user_films": user_films})


@login_required
def upload_film_photo(request, pk):
    photo = request.FILES.get("photo")
    user_film = get_object_or_404(UserFilms, pk=pk)
    user_film.film.photo.save(photo.name, photo)

    return render(request, "partials/film-detail.html", {"user_film": user_film})

