from django.db import models

from satisfaction.satisfaction import analyze_satisfaction


class Contact(models.Model):
    """
    Represents a contact form submission.

    Attributes:
        first_name (str): The sender's first name.
        last_name (str): The sender's last name.
        phone_number (str): The sender's phone number.
        email_address (str): The sender's email address.
        message (str): The content of the contact message.
        created_at (datetime): Timestamp automatically set when the message is
        created.
        updated_at (datetime): Timestamp automatically updated when the message
        is modified.
        satisfaction (int | None): Optional numeric sentiment score,
        automatically derived from the message.
    """

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(20)
    email_address = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    satisfaction = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically analyze satisfaction from the
        message content.

        If a message is provided, calls `analyze_satisfaction` to compute
        a sentiment or satisfaction score and assigns it to the `satisfaction`
        field
        before saving the instance.

        Args:
            *args: Variable-length argument list passed to the parent save
            method.
            **kwargs: Arbitrary keyword arguments passed to the parent save
            method.
        """

        if self.message:
            self.satisfaction = analyze_satisfaction(self.message)
        super().save(*args, **kwargs)
