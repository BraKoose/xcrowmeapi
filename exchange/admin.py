from django.contrib import admin

from .models import Exchange, ExchangeTransaction, Currency

class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('user', 'fund_account_currency', 'exchange_currency', 'exchange_rate', 'amount',)
    search_fields = ('user',)
    list_filter = ('active', 'fund_account_currency', 'exchange_currency',)

class ExchangeTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_account_currency', 'get_exchange_currency', 'amount',)
    search_fields = ('user',)
    list_filter = ('status', 'thumbs_up',)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'value',)
    search_fields = ('name', 'symbol',)


admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(ExchangeTransaction, ExchangeTransactionAdmin)
admin.site.register(Currency, CurrencyAdmin)