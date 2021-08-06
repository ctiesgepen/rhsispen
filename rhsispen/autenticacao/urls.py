from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.urls import reverse_lazy

app_name = 'autenticacao'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
    	template_name='autenticacao/login.html'),
    	name='login'),

    path('', views.sair,name='logout'),

    path('cadastro/',views.cadastro,name='cadastro'),

    path('alterar_senha/',auth_views.PasswordChangeView.as_view(
        template_name='autenticacao/alterar_senha.html',
        success_url=reverse_lazy('autenticacao:logout')
        ),name='alterar_senha'),
   
    #path('password_reset/', auth_views.PasswordResetView.as_view(
    #    template_name='autenticacao/password_reset_form.html',
    #    success_url=reverse_lazy('autenticacao:password_reset_done')), name='password_reset'),
    
    path('password_reset/',views.password_reset_request,name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='autenticacao/password_reset_done.html'
        ), name='password_reset_done'),
   
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
        template_name='autenticacao/password_reset_confirm.html',
        ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='autenticacao/password_reset_complete.html',
        ), name='password_reset_complete'),

]