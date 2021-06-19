from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'auth'
urlpatterns = [
	path('register/', views.RegisterAPIView.as_view(), name='register'),
	path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),

	# Path for changing user password
	path('user/forgetPassword/', views.ForgetChangePasswordView.as_view(), name='forget_password'),
	path('user/changePassword/', views.ChangePasswordView.as_view(), name='change_password'),

	# Get user verify token for email verification
	path('token/generate/', views.GenerateTokenView.as_view(), name='gen_token'),
	path('token/validate/', views.ValidateTokenView.as_view(), name='validate_token'),

	# Path for generating otp
	path('generate_otp/', views.GenerateOtpView.as_view(), name='gen_otp'),

	# Paths for getting and finding user informations
	path('users/', views.UserListView.as_view(), name='user_list'),
	path('users/detail/<int:id>/', views.UserAPIView.as_view(), name='user_data'),

	# Extra utility paths
	path('user/send-mail/', views.SendMailView.as_view(), name='send_mail'),
	
	# path('verify/login/', login_otp, name='verify_login'),
	# path('logout/', Logout, name='logout'),
	# path('resend-email/', resend_email, name='resend-email'),
]