from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/edit/", views.update_profile, name="edit_profile"),
    path("friends/", views.friends, name="friends"),
    path("post/", views.create_post, name="create_post"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("comment/<int:post_id>/", views.create_comment, name="create_comment"),
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("follow/<str:username>/", views.toggle_follow, name="toggle_follow"),
]
