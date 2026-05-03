from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from .serializers import ContactSerializer


class ContactThrottle(SimpleRateThrottle):
    """Rate-limit contact form submissions per IP, regardless of auth state."""

    scope = "contact"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


@api_view(['POST'])
@throttle_classes([ContactThrottle])
def contact_create(request):
    """
    Handle contact form submissions via POST requests.

    This endpoint allows users to send contact messages.
    Upon receiving valid data, it creates a new `Contact` instance in the
    database.

    Request body (JSON):
        {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+33123456789",
            "email_address": "john@example.com",
            "message": "Your message here..."
        }

    Responses:
        201 Created — When the contact message is successfully saved.
            Returns the serialized contact data.
        400 Bad Request — If validation fails.
            Returns detailed validation error messages.

    Args:
        request (Request): The incoming HTTP request containing contact form
        data.

    Returns:
        Response: A DRF Response object with serialized data or errors.
    """
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
