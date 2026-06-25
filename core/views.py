from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, ProfileForm, RegisterForm
from .models import Comment, Follow, Like, Post, Profile


def landing(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "landing.html")


def home(request):
    posts = Post.objects.select_related("author").prefetch_related("comments__author", "likes").order_by("-created_at")
    post_form = PostForm()
    comment_form = CommentForm()
    suggested_users = User.objects.exclude(id=request.user.id).order_by("?")[:4] if request.user.is_authenticated else User.objects.order_by("?")[:4]
    if request.user.is_authenticated:
        for post in posts:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
    else:
        for post in posts:
            post.user_has_liked = False
    return render(request, "home.html", {
        "posts": posts,
        "post_form": post_form,
        "comment_form": comment_form,
        "suggested_users": suggested_users,
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    return redirect("home")


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect("home")


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
    return redirect(request.META.get("HTTP_REFERER", "home"))


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related("author").prefetch_related("comments__author", "likes"), id=post_id)
    comment_form = CommentForm()
    user_has_liked = post.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
    return render(request, "post_detail.html", {"post": post, "comment_form": comment_form, "user_has_liked": user_has_liked})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=profile_user)
    posts = Post.objects.filter(author=profile_user).select_related("author").prefetch_related("comments__author", "likes").order_by("-created_at")
    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    followers = User.objects.filter(following__following=profile_user)
    following = User.objects.filter(followers__follower=profile_user)
    suggested_users = User.objects.exclude(id=profile_user.id).exclude(id=request.user.id).order_by("?")[:3] if request.user.is_authenticated else User.objects.exclude(id=profile_user.id).order_by("?")[:3]
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
        for post in posts:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
    else:
        for post in posts:
            post.user_has_liked = False
    return render(request, "profile.html", {
        "profile_user": profile_user,
        "profile_obj": profile_obj,
        "posts": posts,
        "follower_count": follower_count,
        "following_count": following_count,
        "followers": followers,
        "following": following,
        "suggested_users": suggested_users,
        "is_following": is_following,
        "comment_form": CommentForm(),
    })


@login_required
def friends(request):
    followers = User.objects.filter(following__following=request.user)
    following = User.objects.filter(followers__follower=request.user)
    suggested_users = User.objects.exclude(id=request.user.id).exclude(id__in=following).order_by("?")[:5]
    return render(request, "friends.html", {
        "followers": followers,
        "following": following,
        "suggested_users": suggested_users,
    })


@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect("profile", username=username)
    follow = Follow.objects.filter(follower=request.user, following=target_user).first()
    if follow:
        follow.delete()
    else:
        Follow.objects.create(follower=request.user, following=target_user)
    return redirect("profile", username=username)


@login_required
def update_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if profile_user != request.user:
        return redirect("profile", username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=profile_user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect("profile", username=username)
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, "edit_profile.html", {"form": form, "profile_user": profile_user})
