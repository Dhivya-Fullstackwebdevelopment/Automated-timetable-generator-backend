from django.urls import path
from .views import generate_timetable

urlpatterns = [
    path('generate/', generate_timetable),
]