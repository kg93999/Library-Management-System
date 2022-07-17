from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager


# NOTE: Delete cookies first before running the program for first time
# Creating custom User and UserManager
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, password2=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username = self.normalize_email(username)
        )

        # user = self.model(username = username)

        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, username, password = None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username,
            password = password,
        )
        user.is_admin = True
        user.save(using = self._db)
        return user



class MyUser(AbstractUser):
    username = models.EmailField(max_length = 70, unique = True)
    password = models.CharField(max_length = 50)
    is_admin = models.BooleanField(default = False)
    create_date = models.DateTimeField(auto_now_add = True)
    update_date = models.DateTimeField(auto_now = True)
    is_active = models.BooleanField(default = True)

    objects = UserManager()
    username = username # None
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username}"   # return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Books(models.Model):
    name = models.CharField(max_length = 100)
    author = models.CharField(max_length = 100)
    isbn_code = models.CharField(max_length = 13, blank = False, unique = True)
    available = models.BooleanField(default = True)     # means deleting a book will change available to false

    def __str__(self):
        return f"{self.name}, {self.author}"

class BookIssued(models.Model):
    to = models.EmailField(max_length = 70, blank = False)   # Here username of student will come
    isbn_code = models.CharField(max_length = 13, blank = False, unique = True)
    issue_date = models.DateField(auto_now = True)
    expiry_date = models.DateField(default = (datetime.today() + timedelta(days = 14)))
    is_borrowed = models.BooleanField(default = False)      # Represent soft delete in database