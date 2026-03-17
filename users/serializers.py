from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, default="123456")
    email = serializers.EmailField(
        error_messages={
            'invalid': 'Por favor, forneça um e-mail válido. Exemplo: usuario@dominio.com.'
        }
    )
    username = serializers.CharField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já foi cadastrado!")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username já foi cadastrado!")
        return value

    class Meta:
        model = CustomUser
        fields = ['email','password', 'username']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            username = validated_data.get('username', '')
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
