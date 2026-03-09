from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import TestCase
from blog.models import Post

User = get_user_model()


class BlogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='Motdepasse123!',
            is_active=True
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='Motdepasse123!',
            is_active=True
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Contenu de test',
            author=self.user1
        )

    def get_token(self, user):
        return str(RefreshToken.for_user(user).access_token)

    def test_list_posts_unauthenticated(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)

    def test_create_post_unauthenticated(self):
        response = self.client.post('/api/posts/', {
            'title': 'Nouveau post',
            'content': 'Contenu'
        })
        self.assertEqual(response.status_code, 401)

    def test_create_post_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user1)}')
        response = self.client.post('/api/posts/', {
            'title': 'Nouveau post',
            'content': 'Contenu du post'
        })
        self.assertEqual(response.status_code, 201)

    def test_update_post_not_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user2)}')
        response = self.client.patch(f'/api/posts/{self.post.slug}/', {
            'title': 'Titre modifié'
        })
        self.assertEqual(response.status_code, 403)

    def test_update_post_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user1)}')
        response = self.client.patch(f'/api/posts/{self.post.slug}/', {
            'title': 'Titre modifié'
        })
        self.assertEqual(response.status_code, 200)
