from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_subject),
    path('list/', views.get_subjects),
    path('update/<int:pk>/', views.update_subject),
    path('delete/<int:pk>/', views.delete_subject),
]