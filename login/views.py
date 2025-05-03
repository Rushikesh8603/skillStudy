from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, RefreshTokenStore, Profile, Earning, KYC, Withdraw
from .serializers import UserSerializer, KYCSerializer, EarningSerializer, WithdrawSerializer
from .utils import send_otp_email



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    RefreshTokenStore.objects.update_or_create(user=user, defaults={'token': str(refresh)})
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """User registration"""
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=400)

    if User.objects.filter(phone=data['phone']).exists():
        return Response({'error': 'Phone number already exists'}, status=400)
    
    if User.objects.filter(referal_id=data['referal_id']).exists():
        user = User.objects.create(
            email=data['email'],
            name=data['name'],
            phone=data['phone'],
            referal_id=data['referal_id'],
            package=data['package'],
        )
        user.set_password(data['password'])
        user.save()

        # email validation
        # send_email_verification(user)


        return Response({'message': 'User registered successfully'}, status=201)
    else:
        return Response({'error': 'Invalid referal id'}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """User login and token generation"""
    data = request.data
    user = authenticate(email=data['email'], password=data['password'])

    if user:
        tokens = get_tokens_for_user(user)
        return Response({'tokens': tokens, 'user': UserSerializer(user).data})
    
    return Response({'error': 'Invalid Credentials'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout and delete the stored refresh token"""
    try:
        token_entry = RefreshTokenStore.objects.get(user=request.user)
        token_entry.revoke()
        return Response({'message': 'User logged out successfully'}, status=200)
    except RefreshTokenStore.DoesNotExist:
        return Response({'error': 'User not logged in'}, status=400)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get authenticated user's profile"""
    user = request.user
    return Response(UserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_earnings(request):
    """Fetch authenticated user's earnings"""
    earnings = Earning.objects.filter(user=request.user)
    serializer = EarningSerializer(earnings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_kyc(request):
    """Fetch authenticated user's KYC details"""
    try:
        kyc = request.user.kyc_details  # Since KYC is OneToOneField
        serializer = KYCSerializer(kyc)
        return Response(serializer.data)
    except KYC.DoesNotExist:
        return Response({'error': 'No KYC found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_withdraws(request):
    """Fetch authenticated user's withdraw history"""
    withdraws = Withdraw.objects.filter(user=request.user)
    serializer = WithdrawSerializer(withdraws, many=True)
    return Response(serializer.data)





@api_view(['POST'])
def send_otp(request):
    """API to send OTP for email verification"""
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=400)

    otp = send_otp_email(email)
    if otp:
        request.session['otp'] = otp  # Store OTP in session (or DB)
        return Response({"message": "OTP sent successfully!"}, status=200)
    else:
        return Response({"error": "Failed to send OTP"}, status=500)
    


@api_view(['POST'])
def verify_otp(request):
    """API to verify the OTP"""
    user_otp = request.data.get("otp")

    if not user_otp:
        return Response({"error": "OTP is required"}, status=400)

    if request.session.get('otp') == user_otp:
        request.session.pop('otp')  # Remove OTP after successful verification
        return Response({"message": "OTP verified successfully!"}, status=200)
    else:
        return Response({"error": "Invalid OTP"}, status=400)
