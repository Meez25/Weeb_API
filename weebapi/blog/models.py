from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    """
    Represents a blog post entry.

    Attributes:
        title (str): The title of the post. Must be unique.
        slug (str): URL-friendly version of the title, automatically generated
        if blank.
        excerpt (str): Optional short summary or preview of the content.
        content (str): The main body text of the post.
        author (str): The author’s name. Defaults to "Anonyme".
        is_published (bool): Indicates whether the post is publicly visible.
        created_at (datetime): Timestamp automatically set when the post is
        created.
        updated_at (datetime): Timestamp automatically updated when the post is
        modified.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    author = models.CharField(max_length=120, default="Anonyme")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata options."""
        ordering = ["-created_at"]  # Display most recent posts first

    def save(self, *args, **kwargs):
        """
        Override the default save method to automatically generate a unique
        slug.

        If the slug field is empty, it creates one from the title using
        Django’s `slugify`.
        If a slug already exists, appends a numeric suffix (-2, -3, etc.) to
        ensure uniqueness.

        Args:
            *args: Variable length argument list passed to the parent class.
            **kwargs: Arbitrary keyword arguments passed to the parent class.
        """
        if not self.slug:
            base = slugify(self.title)
            candidate = base
            i = 1
            while Post.objects.filter(slug=candidate).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a human-readable representation of the Post instance.

        Returns:
            str: The title of the post.
        """
        return self.title
