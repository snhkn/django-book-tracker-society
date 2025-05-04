from django.urls import path
from . import views

app_name ="core"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("profile/<int:pk>", views.profile, name="profile"),
    path('add/', views.add_userbook, name='add_userbook'),
    path('mybooks/', views.my_books, name='my_books'),

]
