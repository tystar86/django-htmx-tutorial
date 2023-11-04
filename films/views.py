from typing import Any
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.shortcuts import render
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
from films.models import Film

# Create your views here.
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
    context_object_name = "films"

    def get_queryset(self) -> QuerySet[Any]:
        user = self.request.user

        return user.films.all()


@login_required
def add_film(request):
    filmname = request.POST.get("filmname")

    film = Film.objects.get_or_create(name=filmname)[0]

    request.user.films.add(film)

    messages.success(request, f"Added <em><b>{filmname}</b></em> to your list of films.")

    return render(request, "partials/film-list.html", {"films": request.user.films.all()})


@login_required
@require_http_methods(["DELETE"])
def remove_film(request, pk):
    request.user.films.remove(pk)

    return render(request, "partials/film-list.html", {"films": request.user.films.all()})


@login_required
def search_film(request):
    search_text = request.POST.get("search")
    user_film_names = request.user.films.all().values_list("name", flat=True)
    results = Film.objects.filter(name__icontains=search_text).exclude(name__in=user_film_names)

    return render(request, "partials/search-results.html", {"results": results})
    

def message_clear(request):
    return HttpResponse("")