# from django.urls import include, path
# from rest_framework import routers
# from . import views

# router = routers.DefaultRouter()
# router.register(r'Simple_c_calc', views.Simple_c_calcViewSet)

# # Wire up our API using automatic URL routing.
# # Additionally, we include login URLs for the browsable API.
# urlpatterns = [
#     path('', include(router.urls)),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]


from django.urls import include, path
from . import views

urlpatterns = [
  path('welcome', views.welcome),
  path('sum_data', views.sum_data),
  path('comp_data', views.comp_data),
]