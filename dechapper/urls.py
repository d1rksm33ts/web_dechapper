from django.urls import path

from . import views

app_name = "dechapper"
urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("health/", views.health, name="health"),
]

