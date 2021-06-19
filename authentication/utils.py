from datetime import datetime
import hashlib
import random
import re
import string

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

def validate_phone(phone=''):
	pattern =r'^\+(?:[0-9] ?){6,14}[0-9]$'
	s=re.match(pattern,phone)
	if s is not None:
		return True

def random_text(p=5):
	return ''.join(random.sample(string.ascii_letters+string.digits,p))

def invalid_str(value):
	# This checks if a string contains special chars or not
	for i in string.punctuation:
		if i in value:
			return True
	return False

def username_gen(n):
    # This will generate a text in this format 'user<n random digits>'
    return 'user'+ ''.join(random.sample(string.digits,n))

def get_usable_name(instance, profile, name=None):
	if not name:
		name = username_gen(5)

    # Check if the name exists in the Profile table
	exists=profile.objects.filter(username=name).exists()
	if exists:
		return get_usable_name(instance, profile, username_gen(5))
	return name

def random_otp(p=6):
	return ''.join(random.sample(string.digits,p))