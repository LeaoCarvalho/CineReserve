from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Creates a new user account.",

        request_body=RegisterSerializer,

        responses={
            201: openapi.Response(
                description="User successfully created"
            ),
            400: openapi.Response(
                description="Validation error"
            ),
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario criado com sucesso"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User login",
        operation_description=(
            "Authenticates a user using email and password. "
            "Returns a JWT access token and sets a refresh token in an HTTP-only cookie."
        ),

        request_body=LoginSerializer,

        responses={
            200: openapi.Response(
                description="Login successful"
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            401: openapi.Response(
                description="Invalid credentials"
            ),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"error": "Credenciais inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
            
        refresh = RefreshToken.for_user(user)
        response = Response({
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key="refreshTokenCertificados",
            value=str(refresh),
            httponly=True,      # não acessível via JS
            secure=True,        # HTTPS obrigatório (em produção)
            samesite="Strict",  # recomendado para segurança
            max_age=24*60*60    # 1 dia
        )
        return response

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description=(
            "Generates a new access token using the refresh token stored in cookies. "
            "The refresh token must be sent automatically via the HTTP-only cookie "
            "'refreshTokenCertificados'. No request body is required."
        ),

        request_body=None,

        responses={
            200: openapi.Response(
                description="New access token generated"
            ),
            401: openapi.Response(
                description="Missing or invalid refresh token"
            ),
        }
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refreshTokenCertificados")
        if not refresh_token:
            return Response({"error": "Refresh token ausente"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
        except TokenError:
            return Response({"error": "Refresh token inválido ou expirado"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"access": new_access}, status=status.HTTP_200_OK)
