from django.urls import path
from . import views

app_name = 'exchange'
urlpatterns = [
	path('deals/', views.ListCreateExchange.as_view(), name='lc_exchange'),
	path('deals/<str:uid>/', views.RUDExchange.as_view(), name='rud_exchange'),
	path('transactions/', views.ListCreateExchangeTransaction.as_view(), name='lc_transaction'),
	path('transactions/<str:uid>/', views.RUDExchangeTransaction.as_view(), name='rud_exchangetransaction'),

    # Currency paths
	path('currency/list/', views.CurrencyList.as_view(), name='list_currency'),
	path('currency/get/<int:id>/', views.CurrencyView.as_view(), name='get_currency'),
]