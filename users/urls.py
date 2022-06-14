from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import(
    registration_view,
    account_properties_view,
	update_account_view,
)

app_name = 'users'

urlpatterns = [
    path('register', registration_view, name="register"),
    path('login', obtain_auth_token, name="login"), # -> see accounts/api/views.py for response and url info
    path('properties', account_properties_view, name="properties"),
	path('properties/update', update_account_view, name="update"),
]