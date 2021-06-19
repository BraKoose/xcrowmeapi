from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# from authentication.models import User

from exchange.models import Exchange, ExchangeTransaction, Currency
from exchange.utils import validate_exchange_amount


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class ExchangeSerializer(serializers.ModelSerializer):
    fund_account_currency = serializers.SlugRelatedField(
        slug_field='symbol',
        queryset = Currency.objects.filter()
    )
    exchange_currency = serializers.SlugRelatedField(
        slug_field='symbol',
        queryset = Currency.objects.filter()
    )

    class Meta:
        model = Exchange
        exclude = ['id']
        read_only_fields = ['uid']
    
    def validate_user(self, value):
        if not self.instance:
            if value.exchange_set.filter(active=True).count() >= settings.EXCHANGE_DEALS_LIMIT:
                raise serializers.ValidationError(F'You can only have {settings.EXCHANGE_DEALS_LIMIT} active deals at a time')
        
        return value
    
    def validate(self, attrs):
        # Get needed info
        currency = attrs['fund_account_currency']

        res, needed = validate_exchange_amount(amount=attrs['amount'], value=currency.value)
        if not res:
            raise serializers.ValidationError(f'Exchange amount is too small, should not be less than {needed} {currency.symbol}')
        
        return attrs

class ExchangeTransactionSerializer(serializers.ModelSerializer):
    exchange = serializers.SlugRelatedField(
        slug_field='uid',
        queryset = Exchange.objects.filter(active=True)
    )
    class Meta:
        model = ExchangeTransaction
        exclude = ['id']
        read_only_fields = ['uid']
    
    def validate(self, attrs):
        user = attrs['user'] 
        exchange = attrs['exchange']
        # If the user owns the exchange, throw an error(User can't buy from himself)
        if user == exchange.user:
            raise serializers.ValidationError({'user': 'You can\'t buy from your deal'})
        
        # Validate the amount if it is more than the exchange amount
        amount = attrs['amount']
        if (amount / exchange.exchange_rate) > exchange.amount:
            raise serializers.ValidationError({'amount': f'Exchanger doesn\'t have up to {amount} {exchange.exchange_currency}'})
        
        return attrs
