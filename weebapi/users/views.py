from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .serializers import UserCreateSerializer, UserSerializer


class RegisterThrottle(AnonRateThrottle):
    """Rate-limit account registration to prevent automated signup abuse."""
    scope = "register"


@api_view(["POST"])
@throttle_classes([RegisterThrottle])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH: true partial update. Missing `username` means "don't touch it"
    # — the previous .get(..., "") wiped the field on every PATCH that
    # didn't explicitly resend it. Email and password are read_only on the
    # serializer, so anything else in the body is silently dropped.
    if "username" not in request.data:
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    serializer = UserSerializer(user, data={"username": request.data["username"]}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
