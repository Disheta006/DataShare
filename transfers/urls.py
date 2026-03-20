from django.urls import path
from .views import transfer

urlpatterns = [
    path('', transfer, name='transfer'),
]