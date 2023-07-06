"""theotherone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
import re

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


def check_config_category_table_exists():
    from django.db import connection
    table_names = connection.introspection.table_names()
    return any(["config_category" in table_name for table_name in table_names])

# urlpatterns must be empty before migration so that django commands work
if check_config_category_table_exists():
    urlpatterns = [
        path('', include('theotherapp.urls')),
        path('user/', include('user.urls')),
        path('admin/', admin.site.urls),
        path('config/', include('config.urls')),
        # Media path
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), serve, kwargs={"document_root": settings.MEDIA_ROOT}
        ),
    ]
else:
    urlpatterns = []
