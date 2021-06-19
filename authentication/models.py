from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .utils import get_usable_name, validate_phone
from .validators import validate_special_char


class UserManager(BaseUserManager):
    def create_user(self, email=None, first_name=None, last_name=None, phoneno=None, password=None, is_active=True, is_staff=False,
                    is_admin=False, *args, **kwargs):
        if not email:
            raise ValueError("Email is required")
        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if not password:
            raise ValueError("Strong password is required")

        user = self.model(
            email=self.normalize_email(email),
            phoneno=phoneno,
            first_name=first_name,
            last_name=last_name
            )
        user.set_password(password)
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.save(using=self._db)
        return user

    def create_staff(self, email, first_name=None, last_name=None, phoneno=None, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, phoneno=phoneno, password=password, is_staff=True)
        return user

    def create_superuser(self, email, first_name=None, last_name=None, phoneno=None, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, phoneno=phoneno, password=password, is_staff=True,
                                is_admin=True)
        return user

    def get_staffs(self):
        return self.filter(staff=True)

    def get_admins(self):
        return self.filter(admin=True)

LEVELS = [
    ('1', 'Level 0'),
    ('2', 'Level 1'),
    ('3', 'Level 2'),
    ('4', 'Level 3'),
]

class User(AbstractBaseUser):
    rejex_phone = RegexValidator(regex=r'^\+(?:[0-9] ?){6,14}[0-9]$', message='Your phone number is not in the right format')
    
    first_name = models.CharField(max_length=15, validators=[validate_special_char])
    last_name = models.CharField(max_length=15, validators=[validate_special_char])
    email = models.EmailField(max_length=255, unique=True)
    phoneno = models.CharField(max_length=16,
        validators=[rejex_phone],
        help_text='Enter a correct phone number',
        null=True,
        blank=True,
    )

    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    level = models.CharField(max_length=1, choices=LEVELS, default='1')
    start_date = models.DateTimeField(auto_now=True)

    # Confirmation fields
    confirmed_phoneno = models.BooleanField(default=False)
    confirmed_id = models.BooleanField(default=False)
    confirmed_address = models.BooleanField(default=False)
    confirmed_email = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["first_name","last_name"]
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def get_level(self):
        return LEVELS[int(self.level)-1][1]

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, fail=True):
        print(message)
        val = send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[self.email], fail_silently=fail)
        return True if val else False

    def convert(self, boolean):
        if boolean:
            return 1
        return 0

    def level_one_status(self):
        status = {0: '0', 1: '50', 2: '100'}
        add = self.convert(self.confirmed_email)+self.convert(self.confirmed_phoneno)
        return status[add]

    def level_two_status(self):
        status = {0: '0', 1: '100'}
        return status[self.convert(self.confirmed_id)]

    def level_three_status(self):
        status = {0: '0', 1: '100'}
        return status[self.convert(self.confirmed_address)]

    def update_level(self):
        status = 0
        if self.confirmed_email and self.confirmed_phoneno:
            status+=1
            if self.confirmed_id:
                status+=1
                if self.confirmed_address:
                    status+=1
        self.level=LEVELS[status][0]

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    
    @property
    def fullname(self):
        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'
    
    def __str__(self):
        return self.fullname

    # Override save method to validate phone field
    def save(self, *args, **kwargs):
        if self.phoneno:
            # First check if this password has been used by anyone
            exists = User.objects.filter(phoneno=self.phoneno).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError('This phone number has been used')
            
            # Validate your phone number
            phoneno = str(self.phoneno).replace(' ','')
            if not validate_phone(phoneno):
                raise ValidationError('Invalid phone number provided', code='invalid_phone')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'


class Profile(models.Model):
    GENDER = (
        ('0','Not selected',),
        ('1','Male',),
        ('2','Female',),
    )

    username = models.CharField(max_length=255, unique=True)
    gender = models.CharField(choices=GENDER, max_length=1, default='0')
    image = models.ImageField(upload_to='profiles', blank=True)
    id_photo = models.ImageField(upload_to='user_ids', blank=True)
    photo = models.ImageField(upload_to='user_faces', blank=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    address = models.TextField(blank=True)
    bank_statement = models.ImageField(upload_to='address', blank=True)

    country = models.CharField(max_length=255,  blank=True)
    state = models.CharField(max_length=255,  blank=True)
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Profile'

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        username = get_usable_name(instance, Profile)
        Profile.objects.create(username=username, user=instance)

@receiver(pre_save, sender=User)
def update_user(sender, instance, **kwargs):
    instance.update_level()

