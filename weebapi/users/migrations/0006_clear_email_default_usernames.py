"""Make `username` unique, NULL-able, and clear all existing values.

The frontend now treats a NULL `username` as "the user has not yet picked
an author name" and prompts for it on first article publication. The field
becomes `unique=True` so display names can't collide.

This is a personal/dev project — no users are preserved. All existing
usernames are wiped to NULL so the new uniqueness constraint applies
cleanly without per-row dedup work.
"""

from django.db import migrations, models


def clear_all_usernames(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.update(username=None)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_is_active"),
    ]

    operations = [
        # Step 1: allow NULL so the wipe in step 2 doesn't violate NOT NULL.
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        # Step 2: wipe all usernames. Reverse is a noop — restoring legacy
        # values would re-collide once uniqueness is enforced.
        migrations.RunPython(
            clear_all_usernames,
            reverse_code=migrations.RunPython.noop,
        ),
        # Step 3: shrink to a sane display-name size and enforce uniqueness.
        # Safe because every row is NULL after step 2.
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
