import uuid
import secrets
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import TimeStampedModel

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email).lower()
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.SUPER_ADMIN)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

def generate_referral_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        OPERATIONS_ADMIN = 'OPERATIONS_ADMIN', 'Operations Admin'
        FINANCE_ADMIN = 'FINANCE_ADMIN', 'Finance Admin'
        SUPPORT_ADMIN = 'SUPPORT_ADMIN', 'Support Admin'
        MARKETING_ADMIN = 'MARKETING_ADMIN', 'Marketing Admin'
        CUSTOMER = 'CUSTOMER', 'Customer'

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, db_index=True)
    
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )
    
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True
    )
    
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False, db_index=True)
    suspension_reason = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['referral_code']),
        ]

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = generate_referral_code()
            while User.objects.filter(referral_code=code).exists():
                code = generate_referral_code()
            self.referral_code = code
        
        # Keep staff status synchronized for admin roles
        if self.role in [
            self.Role.SUPER_ADMIN,
            self.Role.OPERATIONS_ADMIN,
            self.Role.FINANCE_ADMIN,
            self.Role.SUPPORT_ADMIN,
            self.Role.MARKETING_ADMIN,
        ]:
            self.is_staff = True
            
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email

    @property
    def is_admin_role(self):
        return self.role in [
            self.Role.SUPER_ADMIN,
            self.Role.OPERATIONS_ADMIN,
            self.Role.FINANCE_ADMIN,
            self.Role.SUPPORT_ADMIN,
            self.Role.MARKETING_ADMIN,
        ] or self.is_superuser

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
