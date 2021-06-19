from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
	refresh = RefreshToken.for_user(user)
	return {
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}


def url_with_params(url, params):
	"""
	Url is a relative or full link,
	params is a dictionary of key/value pairs of the query parameters
	{id: 3, name: 'John doe'}
	"""
	# Add trailing backslash to url
	if not url.endswith('/'):
		url += '/'

	# Join the key/value pairs into a string 
	assiged = [f'{key}={value}' for key, value in params.items()]
	
	return url + '?' + '&'.join(assiged)