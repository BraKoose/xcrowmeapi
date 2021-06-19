from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response

from project_api_key.permissions import HasStaffProjectAPIKey

from authentication.permissions import IsAuthenticatedAdmin

from exchange.models import Exchange, ExchangeTransaction, Currency

from . import serializers


class CurrencyList(generics.ListAPIView):
    serializer_class = serializers.CurrencySerializer
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def get_queryset(self):
        queryset = Currency.objects.all()
        
        # Check for filtering queries
        query = self.request.query_params
        name = query.get('name', '')
        symbol = query.get('symbol', '')
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset.order_by('name')

class CurrencyView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = serializers.CurrencySerializer
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    def get_queryset(self):
        return Currency.objects.all()

        
class ListCreateExchange(generics.ListCreateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ExchangeSerializer

    def get_queryset(self):
        # We return only active exchange deals
        queryset = Exchange.objects.filter(active=True)
        
        # Check for filtering queries
        query = self.request.query_params
        c1 = query.get('fund_account_currency', '')
        c2 = query.get('exchange_currency', '')
        min_amount = query.get('min_amount', '')
        max_amount = query.get('max_amount', '')
        if c1:
            queryset = queryset.filter(fund_account_currency__symbol__iexact=c1)
        if c2:
            queryset = queryset.filter(exchange_currency__symbol__iexact=c2)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        
        return queryset


class RUDExchange(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'uid'
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ExchangeSerializer

    def get_queryset(self):
        return Exchange.objects.all()


class ListCreateExchangeTransaction(generics.ListCreateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ExchangeTransactionSerializer

    def get_queryset(self):
        return ExchangeTransaction.objects.all()


class RUDExchangeTransaction(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'uid'
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ExchangeTransactionSerializer

    def get_queryset(self):
        return ExchangeTransaction.objects.all()