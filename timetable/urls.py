from django.urls import path
from .views import admin_login, generate_timetable

urlpatterns = [
    path('generate/', generate_timetable),
    path('admin-login/', admin_login),

]