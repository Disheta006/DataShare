from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from .models import OTPVerification
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .models import OTPVerification, User
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from transfers.models import Transfer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import time
from django.conf import settings
import random
import re

# Create your views here.
def home(request):
    return render(request,'core/home.html')

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least 1 uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least 1 lowercase letter"

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least 1 number"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least 1 special character"

    return True, ""

def user_logout(request):
    logout(request)  # clears session + user data
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")  # redirect to login page

@ratelimit(key='ip', rate='5/m', block=True)
def signup(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not all([first_name, last_name, mobile, password, confirm_password]):
            messages.error(request, "All fields are required")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")
        
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect("signup")

        is_valid, error_message = is_strong_password(password)
        if not is_valid:
            messages.error(request, error_message)
            return redirect("signup")

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered")
            return redirect("signup")
        
        if not mobile.isdigit() or len(mobile) < 10:
            messages.error(request, "Enter a valid mobile number")
            return redirect("signup")
        
        terms = request.POST.get("terms")

        if not terms:
            messages.error(request, "You must accept Terms & Privacy Policy")
            return redirect("signup")

        # Delete old OTP
        OTPVerification.objects.filter(mobile=mobile).delete()

        otp = str(random.randint(100000, 999999))

        OTPVerification.objects.create(
            mobile=mobile,
            otp=otp
        )

        # Store user data
        request.session['signup_data'] = {
        "first_name": first_name,
        "last_name": last_name,
        "mobile": mobile,
        "password": password
        }

        # 🔐 OTP controls
        request.session['otp_attempts'] = 0
        request.session['otp_time'] = time.time()
        request.session['otp_last_sent'] = time.time()

        print(f"OTP for {mobile}: {otp}")

        # ✅ Pass OTP in demo mode
        if settings.DEBUG or settings.DEMO_MODE:
            request.session['otp_debug'] = otp

        return redirect("verify_code")

    return render(request,"core/signup.html")

def verify_code(request):
    signup_data = request.session.get("signup_data")

    if not signup_data:
        messages.error(request, "Session expired. Please signup again.")
        return redirect("signup")

    mobile = signup_data["mobile"]

    context = {}

    # ✅ Show OTP in demo mode
    if settings.DEBUG or settings.DEMO_MODE:
        context['otp_debug'] = request.session.get('otp_debug')

    if request.method == "POST":
        entered_otp = request.POST.get("otp").strip()

        otp_record = OTPVerification.objects.filter(mobile=mobile).last()

        if not otp_record:
            messages.error(request, "OTP not found. Please signup again.")
            return redirect("signup")

        # ⛔ Expiry check (DB + session safety)
        if otp_record.is_expired() or time.time() - request.session.get("otp_time", 0) > settings.OTP_EXPIRY_TIME:
            otp_record.delete()
            messages.error(request, "OTP expired.")
            return redirect("signup")

        # ⛔ Attempt limit
        attempts = request.session.get("otp_attempts", 0)
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            otp_record.delete()
            messages.error(request, "Too many attempts. Try again.")
            return redirect("signup")

        # ✅ Correct OTP
        if str(otp_record.otp) == str(entered_otp):

            user = User.objects.create_user(
                first_name=signup_data["first_name"],
                last_name=signup_data["last_name"],
                mobile=signup_data["mobile"],
                password=signup_data["password"]
            )

            otp_record.delete()

            # Clear session safely
            for key in ["signup_data", "otp_attempts", "otp_time", "otp_debug"]:
                request.session.pop(key, None)

            auth_login(request, user)

            messages.success(request, "Account created successfully")
            return redirect("login")

        # ❌ Wrong OTP
        request.session["otp_attempts"] = attempts + 1
        messages.error(request, "Invalid OTP")

    return render(request, "core/verify_code.html", context)

def resend_otp(request):
    import time
    from django.conf import settings

    signup_data = request.session.get("signup_data")

    if not signup_data:
        messages.error(request, "Session expired")
        return redirect("signup")

    mobile = signup_data["mobile"]

    last_sent = request.session.get("otp_last_sent")

    # ⛔ Cooldown
    if last_sent and time.time() - last_sent < settings.OTP_RESEND_COOLDOWN:
        messages.error(request, "Please wait before requesting another OTP")
        return redirect("verify_code")

    # Generate new OTP
    otp = str(random.randint(100000, 999999))

    OTPVerification.objects.filter(mobile=mobile).delete()

    OTPVerification.objects.create(
        mobile=mobile,
        otp=otp
    )

    request.session['otp_time'] = time.time()
    request.session['otp_last_sent'] = time.time()
    request.session['otp_attempts'] = 0

    print(f"Resent OTP for {mobile}: {otp}")

    if settings.DEBUG or settings.DEMO_MODE:
        request.session['otp_debug'] = otp

    messages.success(request, "OTP resent successfully")

    return redirect("verify_code")

@ratelimit(key='ip', rate='5/m', block=True)
def login(request):

    if request.method == "POST":

        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        user = authenticate(request, mobile=mobile, password=password)

        if user is not None:

            auth_login(request, user)

            if remember == "on":
                # Persist session (2 weeks or whatever SESSION_COOKIE_AGE is)
                request.session.set_expiry(1209600)
            else:
                # Expire when browser closes
                request.session.set_expiry(0)

            return redirect("dashboard")

        else:
            messages.error(request, "Invalid mobile or password")

    return render(request, "core/login.html")

@ratelimit(key='ip', rate='5/m', block=True)
def forget_password(request):

    if request.method == "POST":
        mobile = request.POST.get("mobile").strip()

        # Check if user exists
        if not User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number not registered")
            return redirect("forget_password")

        # Delete old OTPs
        OTPVerification.objects.filter(mobile=mobile).delete()

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        OTPVerification.objects.create(
            mobile=mobile,
            otp=otp
        )

        # Store session
        request.session['reset_mobile'] = mobile
        request.session['reset_otp_attempts'] = 0

        # ✅ ADD THESE
        request.session['reset_otp_time'] = time.time()
        request.session['reset_otp_last_sent'] = time.time()

        print(f"RESET OTP: {otp}")    # Replace this with SMS API later

        # ✅ Demo mode
        if settings.DEBUG or settings.DEMO_MODE:
            request.session['reset_otp_debug'] = otp

        return redirect("verify_reset_otp")

    return render(request, "core/forget_password.html")

def verify_reset_otp(request):
    mobile = request.session.get("reset_mobile")

    if not mobile:
        messages.error(request, "Session expired. Try again.")
        return redirect("forget_password")

    context = {}

    # ✅ Demo OTP display
    if settings.DEBUG or settings.DEMO_MODE:
        context['otp_debug'] = request.session.get('reset_otp_debug')

    if request.method == "POST":
        entered_otp = request.POST.get("otp").strip()

        otp_record = OTPVerification.objects.filter(mobile=mobile).last()

        # 🔴 OTP not found
        if not otp_record:
            messages.error(request, "Invalid request. Try again.")
            return redirect("forget_password")

        # ⛔ Expiry check (DB + session)
        if otp_record.is_expired() or time.time() - request.session.get("reset_otp_time", 0) > settings.OTP_EXPIRY_TIME:
            otp_record.delete()
            messages.error(request, "OTP expired")
            return redirect("forget_password")

        # ⛔ Attempt limiting
        attempts = request.session.get("reset_otp_attempts", 0)

        if attempts >= settings.OTP_MAX_ATTEMPTS:
            otp_record.delete()
            messages.error(request, "Too many attempts. Try again.")
            return redirect("forget_password")

        # ✅ Validate OTP
        if str(otp_record.otp) == str(entered_otp):

            request.session['otp_verified'] = True

            otp_record.delete()

            # Clean session (important)
            for key in ["reset_otp_attempts", "reset_otp_time", "reset_otp_debug"]:
                request.session.pop(key, None)

            return redirect("reset_password")

        else:
            request.session['reset_otp_attempts'] = attempts + 1
            messages.error(request, "Invalid OTP")

    return render(request, "core/verify_reset_otp.html", context)

def reset_password(request):

    mobile = request.session.get("reset_mobile")
    otp_verified = request.session.get("otp_verified")

    if not mobile or not otp_verified:
        messages.error(request, "Unauthorized access")
        return redirect("forget_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("reset_password")

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("forget_password")

        # 🔐 Set new password
        user.set_password(password)
        user.save()

        # Clear session
        request.session.pop("reset_mobile", None)
        request.session.pop("otp_verified", None)
        request.session.pop("reset_otp_attempts", None)

        messages.success(request, "Password reset successful. Please login.")

        return redirect("login")

    return render(request, "core/reset_password.html")

def resend_reset_otp(request):

    mobile = request.session.get("reset_mobile")

    if not mobile:
        messages.error(request, "Session expired")
        return redirect("forget_password")

    last_sent = request.session.get("reset_otp_last_sent")

    # ⛔ Cooldown
    if last_sent and time.time() - last_sent < settings.OTP_RESEND_COOLDOWN:
        messages.error(request, "Please wait before requesting another OTP")
        return redirect("verify_reset_otp")

    otp = str(random.randint(100000, 999999))

    OTPVerification.objects.filter(mobile=mobile).delete()

    OTPVerification.objects.create(
        mobile=mobile,
        otp=otp
    )

    request.session['reset_otp_time'] = time.time()
    request.session['reset_otp_last_sent'] = time.time()
    request.session['reset_otp_attempts'] = 0

    print(f"Resent RESET OTP for {mobile}: {otp}")

    if settings.DEBUG or settings.DEMO_MODE:
        request.session['reset_otp_debug'] = otp

    messages.success(request, "OTP resent successfully")

    return redirect("verify_reset_otp")

@login_required
def dashboard(request):

    user = request.user

    sent = Transfer.objects.filter(sender=user).order_by('-created_at')[:5]
    received = Transfer.objects.filter(receiver=user).order_by('-created_at')[:5]

    context = {
        "balance": user.data_balance,
        "sent_transfers": sent,
        "received_transfers": received,
    }

    return render(request, "core/dashboard.html", context)

def support(request):
    return render(request,'core/support.html')