from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_userbook, name='add_userbook'),
    path('mybooks/', views.my_books, name='my_books'),
]
