from django.urls import path
from .views import(
    registration_view,
)

app_name = 'users'

urlpatterns = [
    path('register', registration_view, name="register"),
]