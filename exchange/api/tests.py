from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from project_api_key.models import ProjectUserAPIKey, ProjectUser

from authentication.models import User
from authentication.api.utils import url_with_params

from exchange.models import Currency, Exchange, ExchangeTransaction
from .serializers import ExchangeSerializer


"""
**without api key request are tested just once per view
"""
class ExchageTests(APITestCase):
    def setUp(self):
        # Generate new user
        user = User.objects.create_user(
            email='netrobeweb@gmail.com',
            first_name='netro',
            last_name='webby',
            password='randopass'
            )
        user.confirmed_email = True
        user.save()

        # Generate staff api key
        project_user = ProjectUser(name='Test Staff User', staff=True, admin=True)
        project_user.save()
        _, key = ProjectUserAPIKey.objects.create_key(
            name=project_user.name,
            project=project_user)

        # Globalize key
        self.user_key = key

        # Generate currencies
        currency_list = [
            {
                'name': 'Nigerian Naira',
                'symbol': 'NGN',
                'value': 455
            },
            {
                'name': 'US Dollar',
                'symbol': 'USD',
                'value': 1
            },
            {
                'name': 'British Pounds',
                'symbol': 'BUP',
                'value': 0.34
            },
            {
                'name': 'Chinese Yen',
                'symbol': 'YEN',
                'value': 126.56
            },
        ]
        # Loop through test data and create currencies
        for i in currency_list:
            Currency.objects.create(**i)
        
        # Create exchanges
        test_data = [
            {
                "fund_account_currency": "BUP",
                "exchange_currency": "USD",
                "fund_account_name": "My New Account",
                "fund_account_bank": "UBA",
                "amount": 60000.0,
                "exchange_rate": 300.0,
                "user": user.id,
            },
            {
                "fund_account_currency": "NGN",
                "exchange_currency": "USD",
                "fund_account_name": "My New Account",
                "fund_account_bank": "UBA",
                "amount": 23000000.0,
                "exchange_rate": 0.34,
                "user": user.id,
            },
            {
                "fund_account_currency": "BUP",
                "exchange_currency": "NGN",
                "fund_account_name": "My New Account",
                "fund_account_bank": "UBA",
                "amount": 70000.0,
                "exchange_rate": 500.0,
                "user": user.id,
            },
            {
                "fund_account_currency": "YEN",
                "exchange_currency": "NGN",
                "fund_account_name": "My New Account",
                "fund_account_bank": "UBA",
                "amount": 4535600000.0,
                "exchange_rate": 456.0,
                "user": user.id,
            }
        ]

        for i in test_data:
            obj = ExchangeSerializer(data=i)
            obj.is_valid()
            obj.save()
    
    def get_user(self):
        # User created in setUp
        return User.objects.get(email='netrobeweb@gmail.com')

    def test_exchange_count(self):
        user = self.get_user()
        self.assertEqual(Exchange.objects.filter(user=user).count(), 4)

    def test_currency(self):
        """
        Test for listing and retrieving currency information
        with and without api key
        """
        url = reverse('exchange:list_currency')

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key (basic)
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """
        With api key, test for filtering. We will loop through different
        parameters and assertEqual for expected count to fully test for errors
        """
        param_list = [
            {
                'param': {
                    'name': 'Nigerian',
                    'symbol': 'USD'
                },
                'expected_count': 0,
            },
            {
                'param': {
                    'symbol': 'USD'
                },
                'expected_count': 1,
            },
            {
                'param': {
                    'name': 'd',
                },
                'expected_count': 2,
            },
        ]
        for param_obj in param_list:
            gen_url = url_with_params(url, param_obj['param'])
            response = self.client.get(gen_url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), param_obj['expected_count'])
    
    def test_exchange(self):
        """
        Test the listing, creation and validation of exchanges
        """
        url = reverse('exchange:lc_exchange')

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key (basic)
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """
        With api key, test for filtering. We will loop through different
        parameters and assertEqual for expected count to fully test for errors
        """
        param_list = [
            {
                'param': {
                    'fund_account_currency': 'BUP',
                    'exchange_currency': 'NGN',
                },
                'expected_count': 1,
            },
            {
                'param': {
                    'exchange_currency': 'NGN',
                },
                'expected_count': 2,
            },
            {
                'param': {
                    'fund_account_currency': 'BUP',
                    'max_amount': 100000,
                    'min_amount': 1000,
                },
                'expected_count': 2,
            },
        ]
        for param_obj in param_list:
            gen_url = url_with_params(url, param_obj['param'])
            response = self.client.get(gen_url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), param_obj['expected_count'])
    
        """
        Test for validation errors for each bad data
        """
        user = self.get_user()
        correct_data = {
            "fund_account_currency": "USD",
            "exchange_currency": "NGN",
            "fund_account_name": "My New Account",
            "fund_account_bank": "UBA",
            "amount": 60000,
            "exchange_rate": 456.0,
            "user": user.id,
        }
        wrong_data = {
            "fund_account_currency": "fff",
            "exchange_currency": "uuu",
            "fund_account_name": "My%New%RAccount",
            "fund_account_bank": "U^^BTT%#A",
            "amount": (settings.EXCHANGE_MINIMUM - 1),
            "user": 1000,
        }
        for key, value in wrong_data.items():
            """
            For each data in the wrong data we will change the corresponding
            data in the correct data to test for each bad data
            """
            data = correct_data.copy()
            data[key] = value
            response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test for successful creation of the exchange
        response = self.client.post(url, correct_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.exchange_set.count(), 5)
        
        """ Test for the exchange deals creation limit for the user
        <settings.EXCHANGE_DEALS_LIMIT> is the max amount of deals a user
        can create
        """
        response = self.client.post(url, correct_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_exchange_rud(self):
        """
        Test the retrieving, updating and deleting of exchanges
        """
        user = self.get_user()
        test_exchange = user.exchange_set.first()
        url = reverse('exchange:rud_exchange', kwargs={'uid': test_exchange.uid})

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key (basic)
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test for update
        """
        Making the amount greater that the current one because we don't
        really know the details of the test exchange, we are using
        <new_amount = test_exchange.amount * 3> to make sure validation error
        for amount is never thrown
        """
        new_amount = test_exchange.amount * 3
        data = {
            'fund_account_currency': test_exchange.fund_account_currency.symbol,
            'exchange_currency': test_exchange.exchange_currency.symbol,
            'fund_account_name': test_exchange.fund_account_name,
            'fund_account_bank': test_exchange.fund_account_bank,
            'amount': new_amount,
            'exchange_rate': test_exchange.exchange_rate,
            'user': test_exchange.user.id
        }
        response = self.client.put(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('amount'), new_amount)
        self.assertEqual(response.data.get('uid'), test_exchange.uid)

        # Test for delete
        response = self.client.delete(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Exchange.objects.filter(uid__exact=test_exchange.uid).count(), 0)

    def test_exchange_transaction(self):
        """
        Test for the creation of exchange transactions, validatation tests,
        permission tests
        """
        user1 = self.get_user()
        test_exchange = user1.exchange_set.first()
        url = reverse('exchange:lc_transaction')

        # List Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # List With api key (basic)
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create another user
        user2 = User.objects.create_user(
            email='sketcherslodge@gmail.com',
            first_name='john',
            last_name='doe',
            password='newrandopass'
            )

        # Test for all kinds of validation errors
        correct_data = {
            "exchange": test_exchange.uid,
            "amount": 456.0,
            "status": "pending",
            "thumbs_up": None,
            "user": user2.id
        }
        wrong_data = {
            "exchange": 'unavailable-uid',
            # Line of code below is too make sure max exchange amount validation
            # catches it
            "amount": test_exchange.amount * test_exchange.exchange_rate * 2,
            "status": "usd",
            "thumbs_up": 3,
            "user": user1.id
        }
        for key, value in wrong_data.items():
            data = correct_data.copy()
            data[key] = value
            response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test for complete creation of exchange transaction
        response = self.client.post(url, correct_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_exchange_transaction_rud(self):
        """
        Test the retrieving, updating and deleting of exchange transaction
        """
        # 1. Setup data for testing
        # Get a test exchange deal
        user = self.get_user()
        test_exchange = user.exchange_set.first()

        # Create another user
        user2 = User.objects.create_user(
            email='sketcherslodge@gmail.com',
            first_name='john',
            last_name='doe',
            password='newrandopass'
            )

        # Create a new transaction for test exchange for testing
        test_transaction = ExchangeTransaction.objects.create(
            user = user2,
            exchange = test_exchange,
            amount = 456,
            status = 'pending',
        )

        # 2. Starting testing on created transaction
        url = reverse('exchange:rud_exchangetransaction', kwargs={'uid': test_transaction.uid})
        
        # Retrive Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Retrive With api key (basic)
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test for update
        data = {
            "exchange": test_exchange.uid,
            "amount": 456.0,
            "status": "pending",
            "thumbs_up": None,
            "user": user2.id
        }
        response = self.client.put(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('uid'), test_transaction.uid)

        # Test for delete
        response = self.client.delete(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExchangeTransaction.objects.filter(uid__exact=test_transaction.uid).count(), 0)
