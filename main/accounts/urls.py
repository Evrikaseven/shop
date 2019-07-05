from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import UserSignUpView, SignUpDoneView

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='main:index'), name='logout'),
    path('accounts/password_change/',
         auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('main:password_change_done')),
         name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/signup/', UserSignUpView.as_view(), name='signup'),
    path('accounts/signup/done/', SignUpDoneView.as_view(), name='signup_done'),
]
