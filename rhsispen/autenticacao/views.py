from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from . forms import CadastroForm
from django.contrib import messages
from namp.models import Servidor
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetForm
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator    


@login_required
def sair(request):
    logout(request)
    return redirect('/')	

def cadastro(request, template_name='autenticacao/cadastro.html'):
	if request.method == 'POST':
		form = CadastroForm(request.POST)
		if form.is_valid():
			try:
				servidor = Servidor.objects.get(id_matricula=form.cleaned_data.get('matricula'),cpf=form.cleaned_data.get('cpf'))
				if servidor:
					user = form.save(commit=False)
					if User.objects.filter(email=user.email).exists():
						messages.warning(request, 'O E-MAIL informado pertence aos registros de outro servidor.')
						return render(request, template_name,{'form': form})
					user.save()
					servidor.fk_user = user
					servidor.save()
			except Servidor.DoesNotExist:
				messages.warning(request, 'Servidor sem cadastro prévio! Verifique CPF, MATRÍCULA e E-MAIL informados ou acione o suporte.')
				return render(request, template_name,{'form': form})
		else:
			return render(request, template_name,{'form': form})	
		messages.info(request, 'Cadastro realizado com sucesso!')
		return redirect('/autenticacao/login/')
	else:
		form = CadastroForm()
		return render(request, template_name,{'form': form})

def password_reset_request(request):
	from django.db.models import Q
	from django.utils.encoding import force_bytes, force_text
	from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
	from django.template.loader import render_to_string
	from django.core.mail import send_mail, BadHeaderError

	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Recuperação de Senha"
					email_template_name = "autenticacao/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'sgtsispen.ddns.net:8010',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'nao-responda@sgtsispento.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					messages.success(request, 'Email de recuperação enviado com sucesso!')
					return redirect ("autenticacao:password_reset_done")
			messages.warning(request, 'O email informado não foi encontrado em nossa base de dados!')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="autenticacao/password_reset_form.html", context={"form":password_reset_form})