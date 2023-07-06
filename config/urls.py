from django.urls import path, include

from config import views

app_name = 'config'

urlpatterns = [
    path('', views.database_configuration_view, name="config")
]
