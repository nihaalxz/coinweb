from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    is_admin = serializers.BooleanField(source='is_admin_role', read_only=True)
    wallet_balance = serializers.SerializerMethodField()
    lifetime_earned = serializers.SerializerMethodField()
    lifetime_redeemed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'is_admin',
            'referral_code',
            'is_verified',
            'is_suspended',
            'suspension_reason',
            'is_active',
            'created_at',
            'updated_at',
            'wallet_balance',
            'lifetime_earned',
            'lifetime_redeemed',
        ]
        read_only_fields = [
            'id',
            'role',
            'is_admin',
            'referral_code',
            'is_verified',
            'is_suspended',
            'suspension_reason',
            'created_at',
            'updated_at',
            'wallet_balance',
            'lifetime_earned',
            'lifetime_redeemed',
        ]

    def get_wallet_balance(self, obj):
        wallet = getattr(obj, 'wallet', None)
        return wallet.coin_balance if wallet else 0

    def get_lifetime_earned(self, obj):
        wallet = getattr(obj, 'wallet', None)
        return wallet.lifetime_earned if wallet else 0

    def get_lifetime_redeemed(self, obj):
        wallet = getattr(obj, 'wallet', None)
        return wallet.lifetime_redeemed if wallet else 0

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    referred_by_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number',
            'referred_by_code',
        ]

    def create(self, validated_data):
        referred_by_code = validated_data.pop('referred_by_code', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Handle referral attribution if code provided
        if referred_by_code:
            from referrals.models import Referral
            try:
                referrer = User.objects.get(referral_code=referred_by_code.strip().upper())
                if referrer.id != user.id:
                    Referral.objects.create(
                        referrer=referrer,
                        referred_user=user,
                        referral_code_used=referred_by_code.strip().upper(),
                    )
            except Exception:
                pass  # Do not block registration on invalid referral code

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            if user.is_suspended:
                raise serializers.ValidationError(f'User account is suspended. Reason: {user.suspension_reason or "Policy violation."}')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Both email and password are required.')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'role',
            'is_verified',
            'is_suspended',
            'suspension_reason',
            'is_active',
        ]
