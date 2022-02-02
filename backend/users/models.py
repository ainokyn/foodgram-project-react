from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('guest', 'Гость'),
    ('admin', 'Администратор'),
)


class MyUserManager(BaseUserManager):
    """Handler for custom user."""
    use_in_migrations = True

    def create_user(self, email, username,
                    first_name, last_name, password=None,
                    is_active=True,
                    is_staff=False, is_admin=False):
        """Creates and saves a User with the given email and password. """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,  email, username, first_name, last_name,
                         password=None):
        """Creates and saves a superuser with the given email and password."""
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
             )
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    """The model of custom user."""
    email = models.EmailField(unique=True, max_length=254, blank=False,
                              null=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='role'
    )
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin' or self.is_superuser

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
