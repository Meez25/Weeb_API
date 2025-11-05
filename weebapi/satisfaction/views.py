from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .satisfaction import analyze_satisfaction_binary


class SatisfactionAPIView(APIView):
    """
    API endpoint for analyzing the satisfaction (sentiment) of a given message.

    Expects a POST request containing a 'message' field in the JSON body.
    Returns a satisfaction score:
        - 1 → Positive sentiment
        - 0 → Negative or neutral sentiment

    Example request:
        POST /api/satisfaction/
        {
            "message": "Je suis très satisfait de votre service !"
        }

    Example success response:
        HTTP 200 OK
        {
            "satisfaction": 1
        }

    Example error response:
        HTTP 400 Bad Request
        {
            "error": "'message' field is required."
        }
    """

    def post(self, request):
        """
        Handle POST requests for sentiment analysis.

        Validates the input, extracts the 'message' field,
        and uses `analyze_satisfaction_binary()` to return a sentiment score.

        Args:
            request (Request): The incoming HTTP request containing JSON data.

        Returns:
            Response: A JSON object containing either:
                - {"satisfaction": int} on success
                - {"error": str} on invalid input
        """
        message = request.data.get("message")

        if message is None:
            return Response(
                {"error": "'message' field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = analyze_satisfaction_binary(message)
        return Response({"satisfaction": result}, status=status.HTTP_200_OK)
