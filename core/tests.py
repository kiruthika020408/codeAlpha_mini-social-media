import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import RegisterForm
from .models import Post


class RegisterFormTests(TestCase):
    def test_username_must_be_at_least_8_characters(self):
        form = RegisterForm(data={
            "username": "short",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("Username must be at least 8 characters long.", form.errors["username"])


class PostImageUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="secret123")

    def test_user_can_create_post_with_image(self):
        image_file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(image_file, format="PNG")
        image_file.seek(0)
        uploaded_image = SimpleUploadedFile("test.png", image_file.read(), content_type="image/png")
        self.client.login(username="tester", password="secret123")

        response = self.client.post(reverse("create_post"), {"content": "Hello world", "image": uploaded_image}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(author=self.user, content="Hello world").exists())
        post = Post.objects.get(author=self.user, content="Hello world")
        self.assertTrue(post.image.name)


class SocialInteractionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="secret123")
        self.other_user = User.objects.create_user(username="authoruser", password="secret123")
        self.post = Post.objects.create(author=self.other_user, content="A post for testing")

    def test_profile_page_shows_like_and_comment_controls(self):
        self.client.login(username="viewer", password="secret123")
        response = self.client.get(reverse("profile", args=[self.other_user.username]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("toggle_like", args=[self.post.id]))
        self.assertContains(response, "Comment")
        self.assertContains(response, reverse("create_comment", args=[self.post.id]))

    def test_user_can_follow_profile_owner(self):
        self.client.login(username="viewer", password="secret123")
        response = self.client.get(reverse("toggle_follow", args=[self.other_user.username]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.following.filter(following=self.other_user).exists())
