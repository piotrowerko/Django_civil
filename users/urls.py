from django.urls import path
#from rest_framework.authtoken.views import obtain_auth_token  # zmiana systemu logowania na custom
from .views import(
    registration_view,
    account_properties_view,
	update_account_view,
    ObtainAuthTokenView,
    does_account_exist_view,
    ChangePasswordView,
    DeleteAccountView,
)

app_name = 'users'

urlpatterns = [
    path('register', registration_view, name="register"),
    #path('login', obtain_auth_token, name="login"), # -> see accounts/api/views.py for response and url info
    path('login', ObtainAuthTokenView.as_view(), name="login"),
    path('properties', account_properties_view, name="properties"),
    path('properties/update', update_account_view, name="update"),
    path('check_if_account_exists', does_account_exist_view, name="check_if_account_exists"),
    path('change_password', ChangePasswordView.as_view(), name="change_password"),
    path('delete_account', DeleteAccountView.as_view(), name="delete_account"),
]