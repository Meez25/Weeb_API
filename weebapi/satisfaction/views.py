from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .satisfaction import analyze_satisfaction


class SatisfactionAPIView(APIView):
    """
    Receives a POST with a 'message' and returns satisfaction: 0 ou 1
    """

    def post(self, request):
        message = request.data.get("message", "")
        result = analyze_satisfaction(message)
        return Response({"satisfaction": result}, status=status.HTTP_200_OK)
