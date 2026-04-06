from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_department),
    path('list/', views.get_departments),
    path('update/<int:pk>/', views.update_department),
    path('delete/<int:pk>/', views.delete_department),
]