import tempfile
import json
from typing import Pattern
import xlwt
from django.shortcuts import render, redirect, get_object_or_404

from .models import Equipe, Servidor, TipoJornada, Jornada, HistAfastamento
from django.http import HttpResponse, HttpResponseRedirect
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from .forms import *
from django.urls import resolve
from urllib.parse import urlparse
from datetime import timedelta as TimeDelta, datetime as DateTime, date as Date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re


from django.core.paginator import Paginator

from django.core.paginator import Paginator


from django.contrib.admin.views.decorators import staff_member_required



@login_required(login_url='/autenticacao/login/')
def home(request,template_name='home.html'):
    return render(request,template_name, {'servidor':Servidor.objects.get(fk_user=request.user.id)})



@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_operador_att_form(request, id_equipe):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		equipe = Equipe.objects.get(id_equipe=id_equipe)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Equipe.DoesNotExist:
		messages.warning(request, 'Equipe não encontrada!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	form = EquipeForm(instance=equipe)
	if request.method == 'POST':
		form = EquipeForm(request.POST, instance=equipe)
		if form.is_valid():
			'''
			Realizar os tratamentos necessários e fazer o form.save()
			para a instância do modelo Equipe seja salva
			'''
			form.save()
			messages.success(request, 'Equipe editada com suceso!')
			return HttpResponseRedirect('/equipe_operador_change_list')
		else:
			contexto = {
				'equipe':equipe,
				'servidor': servidor,
				'form': form
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/equipe/equipe_operador_att_form.html',contexto)
	else:
		contexto = {
			'equipe':equipe,
			'servidor': servidor,
			'form': form
		}
		return render(request, 'namp/equipe/equipe_operador_att_form.html',contexto)
		
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_operador_change_list(request, template_name='namp/equipe/equipe_operador_change_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		equipes = Equipe.objects.filter(fk_setor=servidor.fk_setor, deleted_on=None)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Equipe.DoesNotExist:
		messages.warning(request, 'Unidade sem equipes equipes cadastradas no momento!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = EquipeSearchForm(request.POST or None)

	page = request.GET.get('page')
	paginator = Paginator(equipes, 10)
	page_obj = paginator.get_page(page)
	
	contexto = { 
		'equipes': equipes,
		'servidor': servidor,
		'form': form,
		'page_obj': page_obj,
	}
	if request.method == 'POST':
		if form.is_valid():
			equipes2 = []
			print(equipes2)
			pattern = re.compile(form.cleaned_data['nome'].upper())
			for equipe in equipes:
				if pattern.search(equipe.nome.upper()):
					equipes2.append(equipe)
			if equipes2:
				page = request.GET.get('page')
				paginator = Paginator(equipes2, 15)
				page_obj = paginator.get_page(page)
				
				contexto = { 
					'equipes': equipes2,
					'servidor': servidor,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				messages.warning(request, 'Equipe com este nome não encontrada!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_operador_change_form(request, template_name='namp/equipe/equipe_operador_change_form.html'):
	form = EquipeForm()
	try:
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
		form.fields['fk_setor'].initial = setor
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if request.method == 'POST':
		form = EquipeForm(request.POST)		
		if form.is_valid():
			'''
			Realizar os tratamentos necessários e fazer o form.save()
			para a instância do modelo Equipe seja salva
			'''
			form.save()
			messages.success(request, 'Equipe adicionada com suceso!')
			return HttpResponseRedirect('/equipe_operador_change_list')

		else:
			contexto = {
				'setor': setor,
				'form': form,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	else:
		contexto = {
			'setor': setor,
			'form': form
		}
		return render(request,template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def EquipeDeleteView(request, id_equipe):
	equipe = get_object_or_404(Equipe, id_equipe=id_equipe)
	servidores = list(Servidor.objects.filter(fk_equipe=equipe))
	if servidores:
		equipeGeral = get_object_or_404(Equipe, nome='GERAL', fk_setor=equipe.fk_setor)
		if equipeGeral:
			for servidor in servidores:
				servidor.fk_equipe = equipeGeral
				servidor.save()
	equipe.delete()
	messages.success(request, "Equipe deletada com sucesso!")
	return HttpResponseRedirect("/equipe_operador_change_list")

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def servidores_operador_change_list(request,template_name='namp/servidor/servidores_operador_change_list.html'):
	try:
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
		equipes = Equipe.objects.filter(fk_setor=setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Equipe.DoesNotExist:
		messages.warning(request, 'Unidade não possui equipes cadastradas')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = ServidorSearchForm(request.POST or None)
	servidores = []
	for	equipe in equipes:
		for servidor in Servidor.objects.filter(fk_equipe=equipe):
			servidores.append(servidor)

	page = request.GET.get('page')
	paginator = Paginator(servidores, 15)
	page_obj = paginator.get_page(page)

	contexto = { 
		'setor': setor,
		'servidores': servidores,
		'form': form,
		'page_obj': page_obj,
	}

	if request.method == 'POST':
		if form.is_valid():
			servidores2 = []
			pattern = re.compile(form.cleaned_data['nome'].upper())
			for servidor in servidores:
				if pattern.search(servidor.nome.upper()):
					servidores2.append(servidor)
			if servidores2:
				page = request.GET.get('page')
				paginator = Paginator(servidores2, 15)
				page_obj = paginator.get_page(page)

				contexto = { 
					'setor': setor,
					'servidores': servidores2,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				print('entrei no form invalid')
				messages.warning(request, 'Servidor com este nome não encontrado!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
def servidor_operador_att_form(request,id_matricula):
	try:
		user = Servidor.objects.get(fk_user=request.user.id)
		servidor = Servidor.objects.get(id_matricula=id_matricula)
		#enderecoServ = EnderecoServ.objects.get(fk_servidor=id_matricula)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	form = ServidorForm(instance=servidor)

	if request.method == 'POST':
		form = ServidorForm(request.POST,instance=servidor)
		if form.is_valid():
			form.save()
			messages.success(request, 'Servidor editado com suceso!')
			return HttpResponseRedirect('/')
		else:
			contexto = {
				'user': user,
				'servidor': servidor,
				'form': form,
				#'enderecoServ': enderecoServ,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/servidor/servidor_operador_att_form.html',contexto)
	else:
		contexto = {
			'form': form,
			'user':user,
			'servidor': servidor,
			#'enderecoServ':enderecoServ,
		}
		return render(request, 'namp/servidor/servidor_operador_att_form.html',contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def servidor_operador_change_form(request,id_matricula):
	try:
		user = Servidor.objects.get(fk_user=request.user.id)
		servidor = Servidor.objects.get(id_matricula=id_matricula)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	form = ServidorForm(instance=servidor)

	if request.method == 'POST':
		form = ServidorForm(request.POST,instance=servidor)
		if form.is_valid():
			form.save()
			messages.success(request, 'Servidor editado com suceso!')
			return HttpResponseRedirect('/servidores_operador_change_list')
		else:
			contexto = {
				'user': user,
				'servidor': servidor,
				'form': form
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/servidor/servidor_operador_change_form.html',contexto)
	else:
		contexto = {
			'form': form,
			'user':user,
			'servidor': servidor,
		}
		return render(request, 'namp/servidor/servidor_operador_change_form.html',contexto)
			
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def frequencias_operador(request,template_name='namp/frequencia/frequencias_operador.html'):
	print('Acesso view de frequencias_operador!')
	return render(request,template_name, {})

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_change_list(request, template_name='namp/afastamento/afastamento_change_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		afastamentos = HistAfastamento.objects.filter(fk_servidor__fk_setor=servidor.fk_setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	form = AfastamentoSearchForm(request.POST or None)
	
	page = request.GET.get('page')
	paginator = Paginator(list(afastamentos), 15)
	page_obj = paginator.get_page(page)

	contexto = { 
		'servidor': servidor,
		'form': form,
		'page_obj': page_obj,
	}

	if request.method == 'POST':
		if form.is_valid():
			afastamentos2 = []
			pattern = re.compile(form.cleaned_data['servidor'].upper())
			for afastamento in afastamentos:
				if pattern.search(afastamento.fk_servidor.nome.upper()):
					afastamentos2.append(afastamento)
			if afastamentos2:
				page = request.GET.get('page')
				paginator = Paginator(afastamentos2, 15)
				page_obj = paginator.get_page(page)

				contexto = { 
					'servidor': servidor,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				messages.warning(request, 'Sem afastamentos para o servidor informado!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_change_form(request,template_name='namp/afastamento/afastamento_change_form.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
	else:
		servidores = list(Servidor.objects.filter(fk_setor=servidor.fk_setor).values_list('id_matricula', 'nome'))
		form = AfastamentoForm({"servidores":servidores})
	if request.method == 'POST':
		form = AfastamentoForm(request.POST, {"servidores":servidores})
		if form.is_valid():
			form.save()	
			return HttpResponseRedirect('/')
		else:
			contexto['form'] = form
			return render(request, template_name, contexto)
	else:
		contexto = { 
			'servidor': servidor,
			'form': form
		}
		return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_att_form(request, id_hist_afastamento):
	try:
		#servidor = Servidor.objects.get(fk_user=request.user.id)
		afastamentos = HistAfastamento.objects.get(id_hist_afastamento=id_hist_afastamento)
	except HistAfastamento.DoesNotExist:
		messages.warning(request, 'Afastamento não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	form = AfastamentoForm(instance=afastamentos)

	if request.method == 'POST':
		form = AfastamentoForm(request.POST,instance=afastamentos)
		if form.is_valid():
			form.save()
			messages.success(request, 'Afastamento editado com suceso!')
			return HttpResponseRedirect('/afastamento_change_list')
		else:
			contexto = {
				#'servidor': servidor,
				'form': form,
				'afastamentos': afastamentos,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/afastamento/afastamento_att_form.html',contexto)
	else:
		contexto = {
			#'servidor':servidor,
			'form': form,
			'afastamentos': afastamentos,
		}
		return render(request, 'namp/servidor/servidor_operador_att_form.html',contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def jornadas_operador(request,template_name='namp/jornada/jornadas_operador.html'):
	#if request.user.groups.filter(name='Operadores').count():
	#if request.user.is_staff or request.user.is_superuser:
	try:
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	equipes = Equipe.objects.filter(status=True,fk_setor=setor.id_setor)
	tem_plantao12 = False
	tem_plantao24 = False
	tem_plantao48 = False
	for equipe in equipes:
		if equipe.fk_tipo_jornada.carga_horaria < 12:
			continue
		if equipe.fk_tipo_jornada.carga_horaria == 12:
			tem_plantao12 = True
			continue
		if equipe.fk_tipo_jornada.carga_horaria == 24:
			tem_plantao24 = True
			continue
		if equipe.fk_tipo_jornada.carga_horaria == 48:
			tem_plantao48 = True
			continue
	
	form = GerarJornadaRegularForm({"tem_plantao12":tem_plantao12,"tem_plantao24":tem_plantao24, "tem_plantao48":tem_plantao48})
	if request.method == 'POST':
		form = GerarJornadaRegularForm(request.POST,{"tem_plantao12":tem_plantao12,"tem_plantao24":tem_plantao24, "tem_plantao48":tem_plantao48})
		if form.is_valid():
			'''
			Trecho onde se captura a equipe de 12h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''
			if form.cleaned_data['equipe_plantao12h'] != '' and form.cleaned_data['data_plantao12h'] != '':
				equipe12h = equipes.get(
					id_equipe=form.cleaned_data['equipe_plantao12h'])
				data_plantao12h = form.cleaned_data['data_plantao12h']
				equipes12h = list(equipes.filter(
					fk_tipo_jornada__carga_horaria=12).filter(nome__gte=equipe12h))
				equipes12h += list(equipes.filter(
					fk_tipo_jornada__carga_horaria=12).filter(nome__lt=equipe12h))
				fimDoMes = data_plantao12h.replace(day=1,month=data_plantao12h.month+1) - TimeDelta(days=1)
				'''
				Percorrendo as equipes de 24h e chamando a função
				geradora de escalas para cada uma das equipes de plantão
				com tipo de jornada similar do setor atual.
				'''
				for equipe in equipes12h:
					funcaogeraescalaporequipe(
						equipe,
						Servidor.objects.filter(fk_equipe=equipe),
						data_plantao12h,
						fimDoMes)
					'''
					Alterando a data inicial para cada equipe de acordo com
					o seu tipo de jornada. Aqui o intervalo é de 24h
					'''
					data_plantao12h += TimeDelta(hours=equipe.fk_tipo_jornada.carga_horaria)

			'''
			Trecho onde se captura a equipe de 24h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''
			if form.cleaned_data['equipe_plantao24h'] != '' and form.cleaned_data['data_plantao24h'] != '':
				equipe24h = equipes.get(
					id_equipe=form.cleaned_data['equipe_plantao24h'])
				data_plantao24h = form.cleaned_data['data_plantao24h']
				equipes24h = list(equipes.filter(
					fk_tipo_jornada__carga_horaria=24).filter(nome__gte=equipe24h))
				equipes24h += list(equipes.filter(
					fk_tipo_jornada__carga_horaria=24).filter(nome__lt=equipe24h))
				fimDoMes = data_plantao24h.replace(day=1,month=data_plantao24h.month+1) - TimeDelta(days=1)
				'''
				Percorrendo as equipes de 24h e chamando a função
				geradora de escalas para cada uma das equipes de plantão
				com tipo de jornada similar do setor atual.
				'''
				for equipe in equipes24h:
					funcaogeraescalaporequipe(
						equipe,
						Servidor.objects.filter(fk_equipe=equipe),
						data_plantao24h,
						fimDoMes)
					'''
					Alterando a data inicial para cada equipe de acordo com
					o seu tipo de jornada. Aqui o intervalo é de 24h
					'''
					data_plantao24h += TimeDelta(hours=equipe.fk_tipo_jornada.carga_horaria)

			'''--------------------------------------------------------
			Trecho onde se captura a equipe de 48h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''
			if form.cleaned_data['equipe_plantao48h'] != '' and form.cleaned_data['data_plantao48h'] != '':
				equipe48h = equipes.get(
					id_equipe=form.cleaned_data['equipe_plantao48h'])
				data_plantao48h = form.cleaned_data['data_plantao48h']
				equipes48h = list(equipes.filter(
					fk_tipo_jornada__carga_horaria=48).filter(nome__gte=equipe48h))
				equipes48h += list(equipes.filter(
					fk_tipo_jornada__carga_horaria=48).filter(nome__lt=equipe48h))
				fimDoMes = data_plantao48h.replace(day=1,month=data_plantao48h.month+1) - TimeDelta(days=1)
				'''
				Percorrendo as equipes de 48h e chamando a função
				geradora de escalas para cada uma das equipes de plantão
				com tipo de jornada similar do setor atual.
				'''
				for equipe in equipes48h:
					funcaogeraescalaporequipe(
						equipe,
						Servidor.objects.filter(fk_equipe=equipe),
						data_plantao48h,
						fimDoMes)
					'''
					Alterando a data inicial para cada equipe de acordo com
					o seu tipo de jornada. Aqui o intervalo é de 48h
					'''
					data_plantao48h += TimeDelta(hours=equipe.fk_tipo_jornada.carga_horaria)

			'''-----------------------------------------------------------
			Trecho onde se captura as equipes de Expediente do setor atual,
			a data inicial do mês de referência e a data final desse
			mesmo mês.
			'''
			equipesExpediente = list(equipes.filter(
				fk_tipo_jornada__carga_horaria__lt=24))
			inicioDoMes = DateTime.today().replace(day=1, month=DateTime.today().month+1)
			fimDoMes = inicioDoMes.replace(month=inicioDoMes.month+1) - TimeDelta(days=1)
			'''
			Percorrendo as equipes de expediente e chamando a função
			geradora de escalas para cada uma das equipes de expediente
			do setor atual.
			'''
			for equipe in equipesExpediente:
				funcaogeraescalaporequipe(
					equipe,
					Servidor.objects.filter(fk_equipe=equipe),
					inicioDoMes,#A data inicial é a mesma para todas equipes de expediente
					fimDoMes)

			messages.success(request, 'As escalas das equipes desta unidade foram atualizadas com suceso!')
			return redirect('/')
		else:
			contexto = {
			'form':form,
			'equipes':equipes,
			'setor':setor,
			'tem_plantao12': tem_plantao12,
			'tem_plantao24': tem_plantao24,
			'tem_plantao48': tem_plantao48
			}
			messages.warning(request, 'Ops! Verifique os campos do formulário!')
			return render(request, template_name, contexto)
	else:
		contexto = {
			'form':form,
			'equipes':equipes,
			'setor':setor,
			'tem_plantao12': tem_plantao12,
			'tem_plantao24': tem_plantao24,
			'tem_plantao48': tem_plantao48
		}
		return render(request,template_name, contexto)
'''
	Recuperar do banco as equipes da unidade penal escolhida no momento do cadastro de servidor e
	as envia para a página populando o campo select fk_equipe
'''

def get_equipes(request):
	result = list(Equipe.objects.none())
	id_setor = request.GET.get('id_setor', '')
	if (id_setor):
		result = list(Equipe.objects.filter(fk_setor=id_setor).values('id_equipe', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_equipes24h(request):
	result = list(Equipe.objects.none())
	id_setor = request.GET.get('id_setor', '')
	if (id_setor):
		result = list(Equipe.objects.filter(fk_setor=id_setor, fk_tipo_jornada__carga_horaria__in=[24]).values('id_equipe', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_equipes48h(request):
	result = list(Equipe.objects.none())
	id_setor = request.GET.get('id_setor', '')
	if (id_setor):
		result = list(Equipe.objects.filter(fk_setor=id_setor, fk_tipo_jornada__carga_horaria__in=[48]).values('id_equipe', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_tipo_jornada(request):
	result = list(TipoJornada.objects.none())
	id_equipe = request.GET.get('id_equipe', '')
	if (id_equipe):
		equipe = Equipe.objects.get(id_equipe=id_equipe)
		if equipe.categoria == 'Plantão':
			result = list(TipoJornada.objects.filter(carga_horaria__in=[24, 48]).values('carga_horaria', 'tipificacao'))
		elif equipe.categoria == 'Expediente':
			result = list(TipoJornada.objects.filter(carga_horaria__in=[6, 8]).values('carga_horaria', 'tipificacao'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_equipe_servidor(request):
	result = list(Equipe.objects.none())
	id_matricula = request.GET.get('id_matricula', '')
	if (id_matricula):
		result = list(Equipe.objects.filter(fk_setor=Servidor.objects.get(id_matricula=id_matricula).fk_setor).values('id_equipe', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def exportar_pdf(request):
	'''# Model data
		servidores = Servidor.objects.all()
		# Rendered
		html_string = render_to_string('pdf_template.html', {'servidores': servidores})
		html = HTML(string=html_string)
		result = html.write_pdf(target='/tmp/servidores.pdf')

		fs = FileSystemStorage('/tmp')
		with fs.open('servidores.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="servidores.pdf"'
			return response'''
	return response

def definirjornadaregular(request):
	id_setor = request.META.get("HTTP_REFERER").split('/')
	form = DefinirJornadaRegularForm()
	form.fields['setor'].initial = id_setor[6]
	form.fields['equipe'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_setor=id_setor[6]).values_list('id_equipe', 'nome'))
	
	contexto = {
		'definirjornadaregularForm': form,
	}
	return render(request, 'namp/setor/gerarjornadaregular.html', contexto)

# métodos que retorna os dias do intervalo a partir do tipo de jornada
def datasportipodejornada(data_inicial, data_final, tipo_jornada):
	datas = []
	feriados = {
		"anonovo": Date(2021,1,1),
		"tiradentes": Date(2021,4,21),
		"trabalho": Date(2021,5,1),
		"independencia": Date(2021,9,7),
		"nsraparecida": Date(2021,10,12),
		"finados": Date(2021,11,2),
		"republica": Date(2021,11,15),
		"natal": Date(2021,12,25),
	}

	if tipo_jornada == 6 or tipo_jornada == 8:
		intervalo = TimeDelta(days=1)
		while data_inicial <= data_final:
			if data_inicial.weekday() not in (5,6) and data_inicial not in feriados.values():
				datas.append(data_inicial)
			data_inicial+= intervalo
		return datas
	elif tipo_jornada == 12:
		intervalo = TimeDelta(days=2)
		while data_inicial <= data_final:
			print(intervalo)
			datas.append(data_inicial)
			data_inicial+= intervalo
		return datas
	elif tipo_jornada == 24:
		intervalo = TimeDelta(days=4)
		while data_inicial <= data_final:
			datas.append(data_inicial)
			data_inicial+= intervalo
		return datas
	elif tipo_jornada == 48:
		intervalo = TimeDelta(days=8)
		while data_inicial <= data_final:
			datas.append(data_inicial)
			data_inicial+= intervalo
		return datas

def funcaogeraescalaporequipe(equipe, servidores, data_inicial, data_final):
	for servidor in servidores:
		#Verifica se o servidor está ativo
		if servidor.situacao:
			my_inicial = Date.fromordinal(min(data_inicial.toordinal(), data_final.toordinal()))
			my_final = Date.fromordinal(max(data_inicial.toordinal(), data_final.toordinal()))
			datas = datasportipodejornada(my_inicial, my_final, equipe.fk_tipo_jornada.carga_horaria)
			for data in datas:
				jornada = Jornada(data_jornada=data, assiduidade=1, fk_servidor=servidor, fk_equipe=equipe, fk_tipo_jornada=equipe.fk_tipo_jornada)
				jornadas = Jornada.objects.filter(fk_servidor=jornada.fk_servidor,data_jornada=jornada.data_jornada)
				if jornadas:
					continue
				jornada.save()

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def gerarescalaregular(request):
	if request.method == "POST":
		form = DefinirJornadaRegularForm(request.POST)
		if form.is_valid():
			#Verifica se a equipe está ativa
			if Equipe.objects.get(id_equipe=form.cleaned_data['equipe']).status:
				funcaogeraescalaporequipe(
					Equipe.objects.get(id_equipe=form.cleaned_data['equipe']),
					Servidor.objects.filter(fk_equipe=Equipe.objects.get(id_equipe=form.cleaned_data['equipe'])),
					form.cleaned_data['data_inicial'],
					form.cleaned_data['data_final'])
				messages.success(request, 'As jornadas da equipe ' + Equipe.objects.get(id_equipe=form.cleaned_data['equipe']).nome.upper() + ' foram atualizadas com suceso!')
				return HttpResponseRedirect('/admin/namp/setor/'+ form.cleaned_data['setor'] + '/change/')
		else:
			messages.warning(request, 'Ops! Verifique os campos do formulário!')
			return render(request, 'namp/setor/gerarjornadaregular.html', {'definirjornadaregularForm': DefinirJornadaRegularForm(initial={'setor':form.cleaned_data['setor']})})
	else:
		return render(request, 'namp/setor/gerarjornadaregular.html', {'definirjornadaregularForm': DefinirJornadaRegularForm(initial={'setor':form.cleaned_data['setor']})})

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def exportar_jornadas_excel(request):
	#recuperando as jornadas do banco. OBS: apenas as jornadas do mês corrente
	jornadas = Jornada.objects.filter(assiduidade=True).filter(data_jornada__month=Date.today().month).order_by('fk_equipe__fk_setor__nome', 'fk_equipe__nome','fk_servidor__nome','data_jornada')
	if jornadas:
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="jornadas.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Jornadas')

		# largura das colunas
		ws.col(0).width = 256 * 12
		ws.col(1).width = 256 * 9
		ws.col(2).width = 256 * 50
		ws.col(3).width = 256 * 12
		ws.col(4).width = 256 * 15
		ws.col(5).width = 256 * 50
		ws.col(6).width = 256 * 18
		ws.col(7).width = 256 * 18
		ws.col(8).width = 256 * 18
		
		#cabeçalho, primeira linha
		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['MATRICULA', 'VINCULO', 'SERVIDOR', 'CPF', 'CODIGO', 'SETOR','CARGA_HORARIA', 'INICIO', 'FIM' ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		#aplicando os atributos das jornadas nas células da planilha
		for jornada in jornadas:
			row_num += 1   
			ws.write(row_num, 0, jornada.fk_servidor.id_matricula, font_style)
			ws.write(row_num, 1, jornada.fk_servidor.vinculo, font_style)
			ws.write(row_num, 2, jornada.fk_servidor.nome, font_style)
			ws.write(row_num, 3, jornada.fk_servidor.cpf, font_style)
			ws.write(row_num, 4, jornada.fk_equipe.fk_setor.id_setor, font_style)
			ws.write(row_num, 5, jornada.fk_equipe.fk_setor.nome, font_style)
			ws.write(row_num, 6, jornada.fk_tipo_jornada.carga_horaria, font_style)
			
			inicio = jornada.data_jornada.strftime("%d/%m/%Y") + " " +jornada.fk_equipe.hora_inicial.strftime("%H:%M:%S")
			ws.write(row_num, 7, DateTime.strptime(inicio, '%d/%m/%Y %H:%M:%S').strftime("%d/%m/%Y %H:%M:%S"), font_style)
			fim = DateTime.strptime(inicio, '%d/%m/%Y %H:%M:%S') + TimeDelta(hours=jornada.fk_tipo_jornada.carga_horaria)
			ws.write(row_num, 8, fim.strftime('%d/%m/%Y %H:%M:%S'), font_style)
		wb.save(response)
		return response
	messages.warning(request, 'Ops! Não há jornadas registradas no mês corrente!')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def exportar_noturno_excel(request):
	#recuperando as jornadas do banco. OBS: apenas as jornadas do mês corrente
	jornadas = Jornada.objects.filter(assiduidade=True).filter(fk_tipo_jornada__carga_horaria__in=[24,48]).order_by('data_jornada','fk_equipe__fk_setor__nome', 'fk_equipe__nome','fk_servidor__nome')
	if jornadas:
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="adicional-noturno.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Adicional')

		# largura das colunas
		ws.col(0).width = 256 * 12
		ws.col(1).width = 256 * 10
		ws.col(2).width = 256 * 30
		ws.col(3).width = 256 * 12
		ws.col(4).width = 256 * 50
		ws.col(5).width = 256 * 15
		ws.col(6).width = 256 * 12
		ws.col(7).width = 256 * 12
		ws.col(8).width = 256 * 25
		
		# Sheet header, first row
		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['NUMFUNC', 'NUMVINC', 'CARGO', 'CPF', 'NOME', 'QUANT(HORAS)', 'DINI', 'DTFIM', 'OBS']

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		def setRow(jornada, hora, dt):
			ws.write(row_num, 0, jornada.fk_servidor.id_matricula, font_style)
			ws.write(row_num, 1, jornada.fk_servidor.vinculo, font_style)
			ws.write(row_num, 2, jornada.fk_servidor.cargo, font_style)
			ws.write(row_num, 3, jornada.fk_servidor.cpf, font_style)
			ws.write(row_num, 4, jornada.fk_servidor.nome, font_style)
			ws.write(row_num, 5, hora, font_style)
			ws.write(row_num, 6, dt, font_style)
			ws.write(row_num, 7, dt, font_style)
			ws.write(row_num, 8, "", font_style)

		#calculo do add
		for jornada in jornadas:
			if jornada.fk_tipo_jornada.carga_horaria == 24:
				if jornada.data_jornada.month==Date.today().month:
					row_num += 1
					setRow(jornada, 2,jornada.data_jornada.strftime("%d/%m/%Y"))
				if Date.fromordinal(jornada.data_jornada.toordinal()+1).month==Date.today().month:
					row_num += 1
					setRow(jornada, 5,Date.fromordinal(jornada.data_jornada.toordinal()+1).strftime("%d/%m/%Y"))			
			elif jornada.fk_tipo_jornada.carga_horaria == 48:
				if jornada.data_jornada.month==Date.today().month:
					row_num += 1
					setRow(jornada, 2,jornada.data_jornada.strftime("%d/%m/%Y"))
				if Date.fromordinal(jornada.data_jornada.toordinal()+1).month==Date.today().month:
					row_num += 1
					setRow(jornada, 7,Date.fromordinal(jornada.data_jornada.toordinal()+1).strftime("%d/%m/%Y"))
				if Date.fromordinal(jornada.data_jornada.toordinal()+2).month==Date.today().month:
					row_num += 1
					setRow(jornada, 5,Date.fromordinal(jornada.data_jornada.toordinal()+2).strftime("%d/%m/%Y"))
		wb.save(response)
		return response
	messages.warning(request, 'Ops! Não há jornadas registradas no mês corrente, para o cálculo do adicional noturno!')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required(login_url='/autenticacao/login/')
def exportar_frequencia_excel(request):
	#recuperando as jornadas do banco. OBS: apenas as jornadas do mês corrente
	jornadas = Jornada.objects.filter(data_jornada__month=Date.today().month).order_by('fk_equipe__fk_setor__nome', 'fk_equipe__nome','fk_servidor__nome','data_jornada')
	histAfastamento = HistAfastamento.objects.filter(fk_servidor=HistAfastamento.fk_servidor)
	if jornadas:
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="frequencia.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Jornadas')

		# largura das colunas
		ws.col(0).width = 256 * 12
		ws.col(1).width = 256 * 9
		ws.col(2).width = 256 * 50
		ws.col(3).width = 256 * 12
		ws.col(4).width = 256 * 15
		ws.col(5).width = 256 * 18
		ws.col(6).width = 256 * 18
		ws.col(7).width = 256 * 18

		#cabeçalho, primeira linha
		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['MATRICULA', 'VINCULO', 'SERVIDOR', 'CPF', 'CODIGO', 'CARGA_HORARIA', 'INICIO', 'FIM', 'OBS' ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		#aplicando os atributos das jornadas nas células da planilha
		for jornada in jornadas:
			row_num += 1   
			ws.write(row_num, 0, jornada.fk_servidor.id_matricula, font_style)
			ws.write(row_num, 1, jornada.fk_servidor.vinculo, font_style)
			ws.write(row_num, 2, jornada.fk_servidor.nome, font_style)
			ws.write(row_num, 3, jornada.fk_servidor.cpf, font_style)
			ws.write(row_num, 4, jornada.fk_equipe.fk_setor.id_setor, font_style)
			ws.write(row_num, 5, jornada.fk_tipo_jornada.carga_horaria, font_style)

			inicio = jornada.data_jornada.strftime("%d/%m/%Y") + " " +jornada.fk_equipe.hora_inicial.strftime("%H:%M:%S")
			ws.write(row_num, 6, DateTime.strptime(inicio, '%d/%m/%Y %H:%M:%S').strftime("%d/%m/%Y %H:%M:%S"), font_style)
			fim = DateTime.strptime(inicio, '%d/%m/%Y %H:%M:%S') + TimeDelta(hours=jornada.fk_tipo_jornada.carga_horaria)
			ws.write(row_num, 7, fim.strftime('%d/%m/%Y %H:%M:%S'), font_style)

			if jornada.data_jornada == HistAfastamento.data_inicial or HistAfastamento.data_final:
				jornada.assiduidade = False
				jornada.fk_afastamento = histAfastamento.fk_afastamento #instance.fk_afastamento = myHistAfastamento.fk_afastamento

			ws.write(row_num, 8, jornada.fk_afastamento, font_style)
		wb.save(response)
		return response
	messages.warning(request, 'Ops! Não há frequências registradas no mês corrente!')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#def busca(self, *args, **kwargs):
#	context = super().busca(*args, **kwargs)
#	query = self.request.GET.get('q')
#	context['query'] = query
	#SearchQuery.objects.create(query=query)
##	return context
