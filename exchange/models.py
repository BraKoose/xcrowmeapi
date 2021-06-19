from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from authentication.models import User
from authentication.validators import validate_special_char

from .utils import validate_exchange_amount, get_usable_uid


class Currency(models.Model):
    name = models.CharField(max_length=64, validators=[validate_special_char])
    # This is the value of the currency for a dollar
    value = models.FloatField(default=0.0, verbose_name='Value per dollar')
    symbol = models.CharField(max_length=10, unique=True, validators=[validate_special_char])

    def __str__(self):
        return self.symbol

    class Meta:
        verbose_name_plural = 'Currencies'

class Exchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fund_account_name = models.CharField(max_length=25, validators=[validate_special_char])
    fund_account_bank = models.CharField(max_length=25, validators=[validate_special_char])
    fund_account_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='fund_currency')
    # This is the amount of currency in account
    amount = models.FloatField()
    exchange_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    """
    Exchange rate works in a simple way, it reads like
    how many <'exchange_currency'> for <'fund_account_currency'>,
    ---Example if the <fund_account_currency = 'USD'> and the
    <exchange_currency = 'YEN'>, and the <exchange_rate = 125>, that means
    it reads 125 YEN / USD 
    """
    exchange_rate = models.FloatField()
    exchange_address = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

    """active field is used to help the owner deactivate or activate the exchange
    deal when he doesn't need or needs it, instead of deleting and creating the
    same thing again"""
    active = models.BooleanField(default=True)

    # Basic unique identifier for most models
    uid = models.CharField(max_length=16, unique=True, blank=True)
    
    def __str__(self):
        return str(self.user)

    # Override save method to validate amount
    def save(self, *args, **kwargs):
        # Validate the exchange amount condition
        currency = self.fund_account_currency
        res, needed = validate_exchange_amount(amount=self.amount, value=currency.value)
        if not res:
            raise ValidationError(f'Exchange amount is too small, should not be less than {needed} {currency.symbol}')
        
        # Validate for deals limit condition
        if self.user.exchange_set.filter(active=True).exclude(uid=self.uid).count() >= settings.EXCHANGE_DEALS_LIMIT:
            raise ValidationError(f'You can only have {settings.EXCHANGE_DEALS_LIMIT} active deals at a time')
        
        # Save the instance
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['created']


class ExchangeTransaction(models.Model):
    STATUS = [
        ('pending', 'Pending',),
        ('completed', 'Completed',)
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    # This is the amount of currency in account
    amount = models.FloatField()
    status = models.CharField(choices=STATUS, max_length=20)
    thumbs_up = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # Basic unique identifier for most models
    uid = models.CharField(max_length=16, unique=True, blank=True)

    @property
    def get_exchange_currency(self):
        # This is the currency they want from the deal
        return self.exchange.fund_account_currency
    
    @property
    def get_account_currency(self):
        # This is the currency they have for the deal
        return self.exchange.exchange_currency
    
    def __str__(self):
        return self.user.fullname
    
    def save(self, *args, **kwargs):
        # If the user owns the exchange, throw an error(User can't buy from himself)
        if self.user == self.exchange.user:
            raise ValidationError('You can\'t buy from your deal')
        return super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['created']

@receiver(pre_save, sender=Exchange)
def gen_exchange_uid(sender, instance, **kwargs):
    if not instance.uid:
        instance.uid = get_usable_uid(instance=instance)

@receiver(pre_save, sender=ExchangeTransaction)
def gen_exchangetransaction_uid(sender, instance, **kwargs):
    if not instance.uid:
        instance.uid = get_usable_uid(instance=instance)