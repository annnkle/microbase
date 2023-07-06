from django.urls import path, include
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    # TODO: JAKI TEMPLATE TUTAJ? WPISAĆ POPRAWNY
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='user/password_change.html',
            success_url="done"
        ),
        name="password_change"
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='user/password_change_done.html'),
        name="password_change_done",
    ),
    path('', include('django.contrib.auth.urls')),
]
