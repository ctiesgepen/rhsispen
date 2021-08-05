from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackends(BaseBackend):
	def authenticate(self, request, username=None, password=None):
		try:
			user = User.objects.get(Q(username__exact=username) | Q(email__exact=username))
			if user.check_password(password):
				return user
		except User.DoesNotExist:
			return None				
	
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
