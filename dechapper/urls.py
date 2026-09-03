from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "dechapper"
urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("health/", views.health, name="health"),
    path(
        "beheer/login/",
        auth_views.LoginView.as_view(
            template_name="dechapper/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("beheer/", views.manage_availability, name="manage_availability"),
    path("beheer/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
