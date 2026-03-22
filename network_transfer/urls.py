"""
URL configuration for network_transfer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from core.views import dashboard, home, resend_otp, resend_reset_otp, signup, login, forget_password, verify_code, reset_password, support, verify_reset_otp, user_logout

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('signup/',signup,name='signup'),
    path("verify-code/", verify_code, name="verify_code"),
    path('login/',login,name='login'),
    path('forget_password/',forget_password,name='forget_password'),
    path('verify_reset_otp/',verify_reset_otp , name='verify_reset_otp'),
    path('reset_password',reset_password,name='reset_password'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('resend-reset-otp/', resend_reset_otp, name='resend_reset_otp'),
    path('transfer/', include('transfers.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('support',support,name='support'),
    path("logout/", user_logout, name="logout"),
]
