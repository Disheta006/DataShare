import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OTPVerification
from django.contrib.auth import login
from .models import OTPVerification, User
from django_ratelimit.decorators import ratelimit

# Create your views here.
def home(request):
    return render(request,'core/home.html')

def transfer(request):
    data_options = ["50MB", "100MB", "150MB", "200MB", "500MB", "1GB"]
    context = {
        'data_options': data_options
    }
    return render(request,'core/transfer.html', context)

@ratelimit(key='ip', rate='5/m', block=True)
def signup(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered")
            return redirect("signup")
        
        OTPVerification.objects.filter(mobile=mobile).delete()

        otp = str(random.randint(100000,999999))

        OTPVerification.objects.create(
            mobile=mobile,
            otp=otp
        )

        # store user data temporarily
        request.session['signup_data'] = {
            "first_name": first_name,
            "last_name": last_name,
            "mobile": mobile,
            "password": password
        }

        request.session['otp_attempts'] = 0
        print("OTP:", otp)  # replace with SMS API later

        return redirect("verify_code")

    return render(request,"core/signup.html")

# OTP VERIFICATION VIEW
def verify_code(request):

    signup_data = request.session.get("signup_data")

    # Prevent direct access without signup
    if not signup_data:
        messages.error(request, "Session expired. Please signup again.")
        return redirect("signup")

    mobile = signup_data["mobile"]

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        # Limit OTP attempts
        attempts = request.session.get("otp_attempts", 0)

        if attempts >= 5:
            messages.error(request, "Too many OTP attempts. Please signup again.")
            return redirect("signup")

        request.session["otp_attempts"] = attempts + 1

        otp_record = OTPVerification.objects.filter(mobile=mobile).last()

        if not otp_record:
            messages.error(request, "OTP not found. Please signup again.")
            return redirect("signup")

        # Check OTP expiry
        if otp_record.is_expired():
            messages.error(request, "OTP expired. Please signup again.")
            return redirect("signup")

        # OTP validation
        if otp_record.otp == entered_otp:

            user = User.objects.create_user(
                first_name=signup_data["first_name"],
                last_name=signup_data["last_name"],
                mobile=signup_data["mobile"],
                password=signup_data["password"]
            )

            # Delete OTP after successful verification
            otp_record.delete()

            # Clear session data
            request.session.pop("signup_data", None)
            request.session.pop("otp_attempts", None)

            # Login user
            login(request, user)

            messages.success(request, "Account created successfully")

            return redirect("home")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "core/verify_code.html")

def login(request):
    return render(request,'core/login.html')

def forget_password(request):
    return render(request,'core/forget_password.html')

def verify_code(request):
    return render(request,'core/verify_code.html')

def reset_password(request):
    return render(request,'core/reset_password.html')

def support(request):
    return render(request,'core/support.html')