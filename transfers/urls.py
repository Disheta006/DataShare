from django.urls import path
from .views import history, transfer

urlpatterns = [
    path('', transfer, name='transfer'),
    path('history/', history, name='history'),
]