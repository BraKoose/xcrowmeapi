from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from authentication.models import User, Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Get required info for validation
        email = attrs['email']
        password = attrs['password']

        """
        Check that the email is available in the User table
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": 'Details do not match an active account'})
        
        if not user.check_password(password):
            raise serializers.ValidationError({"password": 'Your password is incorrect'})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phoneno',
            'profile'
            ]



class ForgetChangePasswordSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'new_password', 'confirm_password', 'profile',)
        extra_kwargs = {
            'first_name': {'read_only': True},
            'email': {'read_only': True},
            'last_name': {'read_only': True},
        }
        
    def validate(self, attrs):
        # Validate if the provided passwords are similar
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})

        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)

        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'old_password', 'new_password', 'confirm_password', 'profile',)
        extra_kwargs = {
            'first_name': {'read_only': True},
            'email': {'read_only': True},
            'last_name': {'read_only': True},
        }
        
    def validate(self, attrs):
        if not self.instance.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Old password is not correct'})

        # Validate if the provided passwords are similar
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})

        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()

        return instance