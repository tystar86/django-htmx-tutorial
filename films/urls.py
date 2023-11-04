from django.urls import path
from films import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("index/", views.IndexView.as_view(), name="index"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("films/", views.FilmListView.as_view(), name="film_list"),
]

hmtx_views = [
    path("check-username/", views.check_username, name="check_username"),
    path("add-film/", views.add_film, name="add_film"),
    path("remove-film/<int:pk>", views.remove_film, name="remove_film"),
    path("search-film/", views.search_film, name="search_film"),
    path("message-clear/", views.message_clear, name="message_clear"),
]

urlpatterns += hmtx_views