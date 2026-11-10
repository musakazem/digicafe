from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AdminProfile, User


class UserSerializer(serializers.ModelSerializer):
    """The user as the frontend sees it."""

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']
        read_only_fields = fields


def tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


class AdminSignupSerializer(serializers.Serializer):
    """Creates an admin account. Signup only creates admins for now."""

    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    employee_id = serializers.CharField(max_length=50)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Enter your full name.')
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_employee_id(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Enter your employee ID.')
        if AdminProfile.objects.filter(employee_id__iexact=value).exists():
            raise serializers.ValidationError('This employee ID is already registered.')
        return value

    def validate(self, attrs):
        # Run Django's password rules (length, common passwords, similarity to name/email).
        candidate = User(email=attrs['email'], full_name=attrs['full_name'])
        try:
            validate_password(attrs['password'], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            role=User.Role.ADMIN,
        )
        AdminProfile.objects.create(
            user=user,
            employee_id=validated_data['employee_id'],
            department=validated_data.get('department', '').strip(),
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """Email + password → access/refresh tokens, plus the user so the frontend needn't ask again."""

    default_error_messages = {'no_active_account': 'Incorrect email or password.'}

    def validate(self, attrs):
        attrs[self.username_field] = attrs[self.username_field].strip().lower()
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
