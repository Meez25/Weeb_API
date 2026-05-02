from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.utils.text import slugify

CATEGORY_CHOICES = [
    ('technologie', 'Technologie'),
    ('developpement', 'Développement'),
    ('accessibilite', 'Accessibilité'),
    ('performance', 'Performance'),
    ('architecture', 'Architecture'),
    ('education', 'Éducation'),
    ('securite', 'Sécurité'),
    ('alpha_beta', 'Alpha/Beta'),
    ('gadget', 'Gadget'),
    ('design', 'Design'),
    ('autre', 'Autre'),
]


class Post(models.Model):
    """
    Represents a blog post entry.

    Attributes:
        title (str): The title of the post.
        slug (str): URL-friendly version of the title, automatically generated
        if blank.
        excerpt (str): Optional short summary or preview of the content.
        content (str): The main body text of the post.
        author (User): The user who created the post.
        category (str): The category of the post, chosen from predefined choices.
        date (datetime): Optional publication date and time of the post.
        readTime (int): Estimated reading time in minutes. Defaults to 0.
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
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        blank=True
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    date = models.DateTimeField(blank=True, null=True)
    readTime = models.PositiveIntegerField(default=0)
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
        Django's `slugify`.
        If a slug already exists, appends a numeric suffix (-2, -3, etc.) to
        ensure uniqueness.

        Two concurrent saves can both pass the existence check and produce the
        same candidate slug. The DB-level unique constraint catches that; this
        method retries on IntegrityError to avoid surfacing a 500 to the caller.

        Args:
            *args: Variable length argument list passed to the parent class.
            **kwargs: Arbitrary keyword arguments passed to the parent class.
        """
        if self.slug:
            super().save(*args, **kwargs)
            return

        base = slugify(self.title) or "post"
        for attempt in range(10):
            candidate = base if attempt == 0 else f"{base}-{attempt + 1}"
            if Post.objects.filter(slug=candidate).exists():
                continue
            self.slug = candidate
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.slug = ""
                continue
        raise IntegrityError(f"Could not generate a unique slug for title={self.title!r}")

    def __str__(self):
        """
        Return a human-readable representation of the Post instance.

        Returns:
            str: The title of the post.
        """
        return self.title
