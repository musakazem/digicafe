from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import AdminSignupSerializer, LoginSerializer, UserSerializer, tokens_for


class SignupView(generics.GenericAPIView):
    """POST /api/auth/signup/ — create an admin account and sign them in."""

    serializer_class = AdminSignupSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'user': UserSerializer(user).data, **tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — email + password → tokens and user."""

    serializer_class = LoginSerializer
    authentication_classes = []
  

class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — the signed-in user."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
