from django.urls import path
#from rest_framework.authtoken.views import obtain_auth_token  # zmiana systemu logowania na custom
from .views import(
    registration_view,
    account_properties_view,
	update_account_view,
    ObtainAuthTokenView,
)

app_name = 'users'

urlpatterns = [
    path('register', registration_view, name="register"),
    #path('login', obtain_auth_token, name="login"), # -> see accounts/api/views.py for response and url info
    path('login', ObtainAuthTokenView.as_view(), name="login"),
    path('properties', account_properties_view, name="properties"),
	path('properties/update', update_account_view, name="update"),
]