import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from project_api_key.models import ProjectUserAPIKey, ProjectUser

from authentication.models import User
from authentication.api.utils import url_with_params


"""
**without api key request are tested just once per view
"""
class AuthenticationAppTest(APITestCase):
    def setUp(self):
        # Generate new user
        user = User.objects.create(
            email='netrobeweb@gmail.com',
            first_name='netro',
            last_name='webby'
            )
        user.set_password('randopass')
        user.active = True
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

    # Utility functions
    def login_user(self):
        url = reverse('auth:login')
        data = {
            'email': 'netrobeweb@gmail.com',
            'password': 'randopass'
        }
        response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})

        return response.data.get('tokens', '')
    
    def test_user_count(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
    
    def test_user_login(self):
        '''
        Test user login with and with api key permission
        '''
        url = reverse('auth:login')
        data = {
            'email': 'netrobeweb@gmail.com',
            'password': 'randopass'
        }
        # Login with out api key
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Login with api key
        response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_registration(self):
        """
        Test to register user with and without api key
        """
        correct_data = {
            'email': 'sketcherslodge@email.com',
            'first_name': 'Netrobe',
            'last_name': 'webby',
            'password': 'newpass12',
            'password2': 'newpass12'
        }
        url = reverse('auth:register')
        
        # Wrong data without api key
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Wrong data with api key
        wrong_data = {
            'email': 'sketcherslodge',
            'first_name': 'Netrobe000000000000000000',
            'last_name': 'webby;d8$',
            'password': 'pass1234',
            'password2': 'pass12345'
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

        # Correct data with api key
        response = self.client.post(url, correct_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_change_password(self):
        """
        Test to change user password with wrong data (with and without api key)
        and correct data with api key
        """
        # Get access token with login user
        token = self.login_user()['access']

        url = reverse('auth:change_password')
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer '+token)
        data = {
            'old_password': 'wrongpass',
            'new_password': 'randopass',
            'confirm_password': 'randopass'
        }
        # Wrong data without api key
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Wrong data with api key
        response = self.client.put(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        data = {
            'old_password': 'randopass',
            'new_password': 'newpass12',
            'confirm_password': 'newpass12'
        }
        # Correct data with api key
        response = self.client.put(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_otp_generator(self):
        """
        Test otp generator with and without api key
        """
        url = reverse('auth:gen_otp')

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_email_token(self):
        """
        1. Test email token generation and validation with and without api key,
        test for wrong user id,
        We will be using this utility function <url_with_params> to get links
        like this <www.google.com/?id=1> (SO it takes the url and data dict to 
        return <www.google.com/?id=1>)

        2. We will also use the response of the correct request to test validate
        token url view. Test for wrong and right values
        """
        # 1: Generate token view test
        url = reverse('auth:gen_token')
        data = {
            'id': ''
        }

        # Without api key
        response = self.client.get(url_with_params(url, data), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key
        response = self.client.get(url_with_params(url, data), format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # With api key and correct data
        data = {
            'id': 1
        }
        correct_response = self.client.get(url_with_params(url, data), format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(correct_response.status_code, status.HTTP_200_OK)


        # 2: Validate email token view test
        url = reverse('auth:validate_token')

        # a. With wrong data and no api key
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # b. With wrong data and api key
        response = self.client.post(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # c. Get the uid and token from the correct_response
        uidb64 = correct_response.data.get('uidb64', '')
        token = correct_response.data.get('token', '')
        data = {
            'uidb64': uidb64,
            'token': token,
        }
        
        response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_refresh_token(self):
        """
        Test to check the functionality of token refresh
        """
        # Get tokens with login user
        tokens = self.login_user()
        refresh = tokens['refresh']

        url = reverse('auth:token_refresh')
        data = {
            'refresh': 'wrongpass'
        }

        # Wrong data without api key
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Wrong data with api key
        response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            'refresh': refresh
        }
        # Correct data with api key
        response = self.client.post(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_forget_password(self):
        """
        Test for forget user password with wrong data (with and without api key)
        and correct data with api key
        """
        url = reverse('auth:forget_password')
        correct_data = {
            'id': 1,
            'new_password': 'randopass',
            'confirm_password': 'randopass'
        }
        # Without api key
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Wrong data with api key
        clone_data = correct_data.copy()
        clone_data['id'] = ''
        response = self.client.put(url, clone_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Wrong data with api key
        wrong_data = {
            'new_password': 'pass1234',
            'confirm_password': 'pass1234'
        }
        for key, value in wrong_data.items():
            # Check similar code in registration test for comments
            data = correct_data.copy()
            data[key] = value
            response = self.client.put(url, data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Correct data with api key
        response = self.client.put(url, correct_data, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_info(self):
        """
        Test for user information urls (list/retrive) with and without api key
        """
        # 1. User list view api test
        url = reverse('auth:user_list')

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # 2. User Detail api test
        url = reverse('auth:user_data', kwargs={'id': 1})
        err_url = reverse('auth:user_data', kwargs={'id': 0})

        # a. Wrong data without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # b. Wrong data with api key
        response = self.client.get(err_url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # c. correct data with api key
        response = self.client.get(url, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sendmail(self):
        """
        Test for sending mail to user with and without api key
        """
        url = reverse('auth:send_mail')

        # Without api key
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With api key (wrong data)
        response = self.client.get(url, {'id': ''}, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # With api key (correct data)
        response = self.client.get(url, {'id': 1}, format='json', **{'HTTP_BEARER_API_KEY':self.user_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    