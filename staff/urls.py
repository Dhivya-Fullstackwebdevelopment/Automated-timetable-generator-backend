from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_staff),
    path('list/', views.get_staff),
    path('update/<int:pk>/', views.update_staff),
    path('delete/<int:pk>/', views.delete_staff),
]