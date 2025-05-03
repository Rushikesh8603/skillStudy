from django.db import models
from decimal import Decimal
import uuid
from django.contrib.auth.hashers import make_password
from django.db import models
from django.conf import settings


class User(models.Model):
    referal_id = models.CharField(primary_key=True, max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    phone = models.BigIntegerField(unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)  # Should use Django's built-in authentication
    package = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    previous_ref_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)  # Hash password before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    



class RefreshTokenStore(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="refresh_token")
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refresh Token for {self.user.email}"

    def revoke(self):
        self.delete()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    dob = models.DateField()
    pro_photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.name}"


class KYC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    holder_name = models.CharField(max_length=255)
    account_no = models.CharField(max_length=20, unique=True)
    ifsc_code = models.CharField(max_length=20)
    aadhar_no = models.CharField(max_length=12, unique=True)
    pan_no = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kyc_details")

    def __str__(self):
        return f"KYC for {self.user.name}"


class Earning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    weekly_earning = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    monthly_earning = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    daily_earning = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="earnings")

    def __str__(self):
        return f"Earnings for {self.user.name}"


class Withdraw(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    time = models.TimeField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdraws")
    earning = models.ForeignKey(Earning, on_delete=models.CASCADE, related_name="withdraws")

    def __str__(self):
        return f"Withdraw of {self.amount} by {self.user.name}"
