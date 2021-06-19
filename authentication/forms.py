from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User
from .utils import invalid_str

class UserRegisterForm(forms.ModelForm):
	password=forms.CharField(label="Password",
							widget=forms.PasswordInput,
							min_length=8,
							help_text=password_validation.password_validators_help_text_html())
	password2=forms.CharField(label="Confirm password",
							widget=forms.PasswordInput,
							help_text='Must be similar to first password to pass verification')
	class Meta:
		model=User
		fields=("email","first_name","last_name","password","password2",)

	def clean_first_name(self):
		first_name = self.cleaned_data.get('first_name')

		if invalid_str(first_name):
			raise forms.ValidationError('You should not use any special characters')

		return first_name

	def clean_last_name(self):
		last_name = self.cleaned_data.get('last_name')

		if invalid_str(last_name):
			raise forms.ValidationError('You should not use any special characters')

		return last_name

	# Cleaning password one to check if all validations are met
	def clean_password(self):
		ps1=self.cleaned_data.get("password")
		password_validation.validate_password(ps1,None)
		return ps1

	"""Override clean on password2 level to compare similarities of password"""
	def clean_password2(self):
		ps1=self.cleaned_data.get("password")
		ps2=self.cleaned_data.get("password2")
		if (ps1 and ps2) and (ps1 != ps2):
			raise forms.ValidationError("The passwords does not match")
		return ps2
		
	""" Override the default save method to use set_password method to convert text to hashed """
	def save(self, commit=True):
		user=super(UserRegisterForm, self).save(commit=False)
		user.set_password(self.cleaned_data.get("password"))
		if commit:
			user.save()
		return user

	class Meta:
		model=User
		fields=("email","phoneno",'last_name','first_name',"password","active","staff","admin",)
		def clean_password(self):
			# Regardless of what the user provides, return the initial value.
			# This is done here, rather than on the field, because the
			# field does not have access to the initial value
			return self.initial["password"]