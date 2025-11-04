from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Contact model.

    Converts Contact instances into JSON-compatible representations
    and validates input data for creating new contact messages.
    Uses a HyperlinkedModelSerializer to optionally include hyperlinks
    in API responses if a `request` context is provided.

    Fields:
        - first_name: The sender's first name.
        - last_name: The sender's last name.
        - phone_number: The sender's phone number.
        - email_address: The sender's email address.
        - message: The body of the message sent by the user.
    """

    class Meta:
        """
        Meta configuration for ContactSerializer.

        Attributes:
            model (Contact): The model being serialized.
            fields (list[str]): The fields to include in the serialized
            representation.
        """
        model = Contact
        fields = ['first_name', 'last_name',
                  'phone_number', 'email_address', 'message']
