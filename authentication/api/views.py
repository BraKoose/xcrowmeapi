from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

from project_api_key.permissions import HasStaffProjectAPIKey

from authentication.tokens import acount_confirm_token
from authentication.models import User
from authentication.utils import random_otp
from authentication.permissions import IsAuthenticatedAdmin

from . import serializers
from .utils import get_tokens_for_user


# Views below
class GenerateTokenView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def get(self, request, format=None):
        # Get required info from the request handler
        pk = request.query_params.get('id', '')

        # Get the user from the pk
        try:
            user  = User.objects.get(id=pk)
        except (User.DoesNotExist, ValueError):
            raise NotFound(detail='User does not exist')

        uidb64   = urlsafe_base64_encode(force_bytes(user.pk))
        token = acount_confirm_token.make_token(user)

        return Response({
            'uidb64': uidb64,
            'token': token
        }, status=status.HTTP_200_OK)


class ValidateTokenView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def post(self, request, format=None):
        # Get the uid and token from the data passed
        uidb64 = request.data.get('uidb64', '')
        token = request.data.get('token', '')
        try:
            uidb64=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ParseError(detail='Invalid token')

        if user!=None and acount_confirm_token.check_token(user,token):
            user.confirmed_email=True
            user.save()
            return Response({
                'id': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
                }, status=status.HTTP_200_OK)
        else:
            raise ParseError(detail='Invalid token')


class GenerateOtpView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def get(self, request, format=None):
        # Generate a random otp
        otp = random_otp()
        
        return Response({
            'otp': otp
        }, status=status.HTTP_200_OK)


class TokenRefreshView(TokenRefreshView):
    permission_classes = (HasStaffProjectAPIKey,)
    # serializer_class = TokenRefreshLifetimeSerializer

class LoginAPIView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            user = User.objects.get(email=email)

            if user.is_active:
                if user.confirmed_email:
                    # Get the user details with the user serializer
                    s2=serializers.UserSerializer(user)
                    # s2.is_valid()
                    user_details = s2.data
                    return Response({
                        'tokens': get_tokens_for_user(user),
                        'user': user_details
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User email is not yet verified'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Account has been deactivated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPIView(CreateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.RegisterSerializer


class ForgetChangePasswordView(UpdateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ForgetChangePasswordSerializer

    def get_object(self):
        try:
            obj = self.get_queryset().get(id=self.request.data.get('id', ''))
            return obj
        except (User.DoesNotExist, ValueError):
            raise NotFound(detail='User does not exist')

    def get_queryset(self):
        return User.objects.filter(active=True)


class ChangePasswordView(UpdateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ChangePasswordSerializer

    def get_object(self):
        try:
            obj = self.get_queryset().get(id=self.request.user.id)
            return obj
        except (User.DoesNotExist, ValueError):
            raise NotFound(detail='User does not exist')

    def get_queryset(self):
        return User.objects.filter(active=True)


class UserListView(ListAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by('first_name')


class UserAPIView(RetrieveAPIView):
    lookup_field = 'id'
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all()
    
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user is not None:
            return Response(self.get_serializer_class()(user).data)
        return NotFound(detail='User does not exist')


class SendMailView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def get(self, request, format=None):
        # Get the user from the pk passed
        pk = request.query_params.get('id', '')
        try:
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            raise NotFound(detail='User does not exist')

        """
        This will get the subject and the message for
        """
        subject = request.query_params.get('subject', '')
        message = request.query_params.get('message', '')
        sent = user.email_user(subject,message)
        
        return Response({
            'user': pk,
            'sent': sent
        }, status=status.HTTP_200_OK)
