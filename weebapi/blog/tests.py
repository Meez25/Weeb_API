from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from .models import Post


def make_user(email="author@example.com", active=True, first_name="Alice", last_name="Author"):
    user = User.objects.create_user(  # type: ignore[call-arg]
        email=email, password="StrongPass123!", first_name=first_name, last_name=last_name
    )
    user.is_active = active
    user.save()
    return user


def auth_client(client, user):
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")  # type: ignore[attr-defined]


class PostListTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        Post.objects.create(
            title="Published Post",
            content="Content",
            category="technologie",
            author=self.user,
            is_published=True,
        )
        Post.objects.create(
            title="Unpublished Post",
            content="Content",
            category="design",
            is_published=False,
        )

    def test_list_posts_anonymous(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]  # type: ignore[attr-defined]
        self.assertIn("Published Post", titles)
        self.assertNotIn("Unpublished Post", titles)

    def test_search_by_title(self):
        response = self.client.get("/api/posts/?q=Published")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # type: ignore[attr-defined]

    def test_filter_by_author(self):
        response = self.client.get("/api/posts/?author=Alice")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # type: ignore[attr-defined]

    def test_ordering_oldest_first(self):
        Post.objects.create(
            title="Older Post", content="C", category="design", is_published=True
        )
        response = self.client.get("/api/posts/?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_default_ordering_newest_first(self):
        """RG-09: posts are ordered by -created_at by default."""
        newest = Post.objects.create(
            title="Newest Published Post",
            content="C",
            category="design",
            is_published=True,
        )
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]  # type: ignore[attr-defined]
        self.assertEqual(titles[0], newest.title)

    def test_pagination_page_size(self):
        """RG-10: the list is paginated using the configured PAGE_SIZE."""
        from django.conf import settings as dj_settings
        page_size = dj_settings.REST_FRAMEWORK["PAGE_SIZE"]
        # setUp creates 1 published post; add page_size more so we span two pages.
        for i in range(page_size):
            Post.objects.create(
                title=f"Extra Post {i}",
                content="C",
                category="design",
                is_published=True,
            )
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), page_size)  # type: ignore[attr-defined]
        self.assertEqual(response.data["count"], page_size + 1)  # type: ignore[attr-defined]
        self.assertIsNotNone(response.data["next"])  # type: ignore[attr-defined]

    def test_search_by_excerpt(self):
        """RG-11: search matches the excerpt field."""
        Post.objects.create(
            title="Random Title",
            excerpt="A summary that talks about Kubernetes",
            content="No keyword here",
            category="design",
            is_published=True,
        )
        response = self.client.get("/api/posts/?q=Kubernetes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]  # type: ignore[attr-defined]
        self.assertIn("Random Title", titles)

    def test_search_by_content(self):
        """RG-11: search matches the content field."""
        Post.objects.create(
            title="Random Title 2",
            excerpt="No keyword here",
            content="The content describes a topic about Terraform.",
            category="design",
            is_published=True,
        )
        response = self.client.get("/api/posts/?q=Terraform")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]  # type: ignore[attr-defined]
        self.assertIn("Random Title 2", titles)


class PostCreateTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.data = {
            "title": "New Post",
            "content": "Some content",
            "category": "technologie",
            "excerpt": "Short summary",
        }

    def test_create_post_authenticated(self):
        auth_client(self.client, self.user)
        response = self.client.post("/api/posts/", self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(title="New Post")
        self.assertEqual(post.author, self.user)

    def test_create_post_unauthenticated(self):
        response = self.client.post("/api/posts/", self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_slug_auto_generated(self):
        auth_client(self.client, self.user)
        response = self.client.post("/api/posts/", self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("new-post", Post.objects.get(title="New Post").slug)

    def test_create_duplicate_title_gets_unique_slug(self):
        auth_client(self.client, self.user)
        self.client.post("/api/posts/", self.data)
        response = self.client.post("/api/posts/", self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        slugs = list(Post.objects.values_list("slug", flat=True))
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_slug_collision_appends_numeric_suffix(self):
        """RG-04: on slug collision, a numeric suffix -2/-3 is appended."""
        auth_client(self.client, self.user)
        for _ in range(3):
            response = self.client.post("/api/posts/", self.data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        slugs = sorted(Post.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, ["new-post", "new-post-2", "new-post-3"])


class PostDetailTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.post = Post.objects.create(
            title="Detail Post",
            content="Content",
            category="technologie",
            author=self.user,
            is_published=True,
        )

    def test_get_post_anonymous(self):
        response = self.client.get(f"/api/posts/{self.post.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Detail Post")  # type: ignore[attr-defined]

    def test_update_post_authenticated(self):
        auth_client(self.client, self.user)
        response = self.client.patch(
            f"/api/posts/{self.post.slug}/", {"title": "Updated Title"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_update_post_unauthenticated(self):
        response = self.client.patch(
            f"/api/posts/{self.post.slug}/", {"title": "Hacked"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_authenticated(self):
        auth_client(self.client, self.user)
        response = self.client.delete(f"/api/posts/{self.post.slug}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_unauthenticated(self):
        response = self.client.delete(f"/api/posts/{self.post.slug}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_post(self):
        response = self.client.get("/api/posts/does-not-exist/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_field_shows_full_name(self):
        self.user.first_name = "Alice"
        self.user.last_name = "Martin"
        self.user.save()
        response = self.client.get(f"/api/posts/{self.post.slug}/")
        self.assertEqual(response.data["author"], "Alice Martin")  # type: ignore[attr-defined]

    def test_author_field_anonyme_when_no_name(self):
        """When the author has no first/last name, never leak the email."""
        noname_user = make_user(email="noname@example.com", first_name="", last_name="")
        post = Post.objects.create(
            title="No Name Post", content="C", category="design",
            author=noname_user, is_published=True,
        )
        response = self.client.get(f"/api/posts/{post.slug}/")
        self.assertEqual(response.data["author"], "Anonyme")  # type: ignore[attr-defined]
        self.assertNotIn(noname_user.email, str(response.data))  # type: ignore[attr-defined]

    def test_author_field_anonyme_when_no_user(self):
        post = Post.objects.create(
            title="No Author", content="C", category="design", is_published=True
        )
        response = self.client.get(f"/api/posts/{post.slug}/")
        self.assertEqual(response.data["author"], "Anonyme")  # type: ignore[attr-defined]
