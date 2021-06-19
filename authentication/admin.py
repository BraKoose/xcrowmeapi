from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserRegisterForm
from .models import User, Profile

class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	# form = UserUpdateForm
	add_form = UserRegisterForm

	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display=('email', 'active', 'level', )
	list_filter = ('active','staff','admin', 'level', 'confirmed_email', 'confirmed_phoneno', 'confirmed_id',)
	search_fields=('email', 'first_name', 'last_name',)
	fieldsets = (
		('User', {'fields': ('email', 'password')}),
		('Profile info', {'fields': ('phoneno','level',)}),
		('Permissions', {'fields': ('admin','staff','active','confirmed_email','confirmed_phoneno','confirmed_id',)}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'first_name', 'last_name', 'phoneno', 'password', 'password2')}
		),
	)
	ordering = ('-start_date',)
	filter_horizontal = ()

class ProfileAdmin(admin.ModelAdmin):
	list_display=('username', 'user', 'country', 'state',)
	search_fields=['username']
	fieldsets=(
		(None, {
			"fields": (
				'user',
				"username",
				"image",
			)
		}),
		("ID information",{
			"classes":("collapse",),
			"fields":(
				'id_photo',
				'photo',
			)
		}),
		("Address information",{
			"classes":("collapse",),
			"fields":(
				'address',
				'country',
				'state',
				'bank_statement',
			)
		})
	)

admin.site.register(User, UserAdmin)

admin.site.register(Profile, ProfileAdmin)