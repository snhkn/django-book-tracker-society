from django.urls import path, include
from . import views

app_name ="core"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("profile/<int:pk>", views.profile, name="profile"),
    path('add/', views.add_userbook, name='add_userbook'),
    path('mybooks/', views.my_books, name='my_books'),
    path("books/<str:status>/", views.filtered_books, name="filtered_books"),
    path('edit-userbook/<int:pk>/', views.edit_userbook, name='edit_userbook'),
    path('delete-userbook/<int:pk>/', views.delete_userbook, name='delete_userbook'),
    path('sign_up/', views.sign_up, name='sign_up'),

]
