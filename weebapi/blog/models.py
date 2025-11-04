from django.db import models
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
        title (str): The title of the post. Must be unique.
        slug (str): URL-friendly version of the title, automatically generated
        if blank.
        excerpt (str): Optional short summary or preview of the content.
        content (str): The main body text of the post.
        author (str): The author’s name. Defaults to "Anonyme".
        category (str): The category of the post, chosen from predefined choices.
        date (datetime): Optional publication date and time of the post.
        readTime (int): Estimated reading time in minutes. Defaults to 0.
        is_published (bool): Indicates whether the post is publicly visible.
        created_at (datetime): Timestamp automatically set when the post is
        created.
        updated_at (datetime): Timestamp automatically updated when the post is
        modified.
    """

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    author = models.CharField(max_length=120, default="Anonyme")
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
