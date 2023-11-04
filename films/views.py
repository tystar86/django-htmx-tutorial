from typing import Any
from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import FormView, TemplateView, ListView
# from django.views.generic.list import ListView
from django.contrib.auth import get_user_model

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
    

class FilmListView(ListView):
    template_name = "films.html"
    model = Film
    context_object_name = "films"

    def get_queryset(self) -> QuerySet[Any]:
        user = self.request.user

        return user.films.all()

    
def add_film(request):
    filmname = request.POST.get("filmname")

    film = Film.objects.create(name=filmname)

    request.user.films.add(film)

    films = request.user.films.all()

    return render(request, "partials/film-list.html", {"films": films})
    