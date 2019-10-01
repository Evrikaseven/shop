from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    UserSignUpView,
    SignUpDoneView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='main/account_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main:index'), name='logout'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('signup/done/<int:pk>', SignUpDoneView.as_view(), name='signup_done'),
]
