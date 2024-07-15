from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reader/<int:reader_id>/", views.reader, name= "Reader"),
    path("user/<int:user_id>/", views.user, name= "User"),
    ]
