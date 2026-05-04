from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    """Signup serializer. `username` is intentionally NOT exposed here so
    clients can't smuggle a display name through registration — the frontend
    prompts for it on first article publication via PATCH /api/users/me/."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Read/update serializer for the current user. Only `username` is
    writable — email and password each have their own dedicated flows."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username"]
        read_only_fields = ["id", "email"]

    def validate_username(self, value):
        # Normalize: strip whitespace, treat blank as NULL. The DB unique
        # constraint allows multiple NULLs but would reject duplicate
        # whitespace-padded variants ("bob" vs "bob "), so we collapse
        # them here before storage.
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        # Case-insensitive uniqueness — Postgres/SQLite unique is case-
        # sensitive by default, which would let "Admin"/"admin"/"ADMIN"
        # all coexist and enable visual impersonation. We keep the case
        # the user picked but reject any iexact collision.
        User = get_user_model()
        qs = User.objects.filter(username__iexact=normalized)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ce nom est déjà utilisé.")
        return normalized
