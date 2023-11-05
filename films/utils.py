from django.db.models import Max
from films.models import UserFilms
from typing import List


def get_order_for_new_film(user) -> int:
    existing_films = UserFilms.objects.filter(user=user)

    if not existing_films.exists():
        return 1
    else:
        current_max = existing_films.aggregate(max_order=Max("order"))["max_order"]

        return current_max + 1


def reorder_films_after_delete(user) -> List[UserFilms]:
    existing_films = UserFilms.objects.filter(user=user)

    if not existing_films.exists():
        return []

    films_count = existing_films.count()
    new_ordering = range(1, films_count + 1)

    for index, user_film in zip(new_ordering, existing_films):
        user_film.order = index
        user_film.save(update_fields=["order"])

    return existing_films

