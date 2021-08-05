import tempfile
import json
from typing import Pattern
import xlwt
from django.shortcuts import render, redirect, get_object_or_404

from .models import Equipe, Servidor, TipoJornada, Jornada, HistAfastamento, PeriodoAcao, EscalaFrequencia, EnderecoServ
from django.http import HttpResponse, HttpResponseRedirect
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from .forms import *
from django.urls import resolve
from urllib.parse import SplitResult, urlparse
from datetime import timedelta as TimeDelta, datetime as DateTime, date as Date, time as Time
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re

from django.core.paginator import Paginator

from django.contrib.admin.views.decorators import staff_member_required

@login_required(login_url='/autenticacao/login/')
def home(request,template_name='home.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	mensagens = {}
	
	#Verificando se tem período para consolidar escalas
	periodo_escala = PeriodoAcao.objects.filter(descricao=1, data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	periodo_frequencia = PeriodoAcao.objects.filter(descricao=2, data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	
	if periodo_escala:
		escalas_geradas = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_escala)
		if not escalas_geradas:
			mensagens['mensagem_escalas'] = 'O período para consolidar as escalas do mês de ' + periodo_escala.data_inicial.strftime('%B') + ' encontra-se em aberto até ' + periodo_escala.data_final.strftime('%d/%m/%Y %H:%M')
			#mensagens.append(mensagem_escalas)
	if periodo_frequencia:
		frequencia_gerada = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_frequencia)
		if not frequencia_gerada:
			mensagens['mensagem_frequencia'] = 'O período para consolidar as frequências do mês de ' + (periodo_frequencia.data_inicial - TimeDelta(days=30)).strftime('%B') + ' encontra-se em aberto até ' + periodo_frequencia.data_final.strftime('%d/%m/%Y %H:%M')		
			#mensagens.append(mensagem_frequencia)
	contexto = {
		'servidor':servidor,
		'mensagens':mensagens
	}
	return render(request,template_name, contexto)

#GESTÃO
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_afastamento(request, template_name='namp/afastamento/admin_afastamento.html'):
	return render(request, template_name)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_servidor(request):
	return render(request, 'admin_servidor.html')

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_setor_criar(request, template_name='namp/setor/admin_setor_criar.html'):
	servidor = Servidor.objects.get(fk_user=request.user.id)
	form = SetorForm()
	try:
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if request.method == 'POST':
		form = SetorForm(request.POST)		
		if form.is_valid():
			form.save()
			messages.success(request, 'Setor adicionada com sucesso!')
			return redirect('namp:admin_setor_list')
		else:
			contexto = {
				'setor': setor,
				'form': form,
				'servidor': servidor,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	else:
		contexto = {
			'setor': setor,
			'form': form,
			'servidor': servidor,
		}
		return render(request,template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_setor_list(request, template_name='namp/setor/admin_setor_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		setores = Setor.objects.all()
	except Setor.DoesNotExist:
		messages.warning(request, 'Setor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
	
	form = SetorSearchForm(request.POST or None)

	page = request.GET.get('page')
	paginator = Paginator(list(setores), 15)
	page_obj = paginator.get_page(page)
	setor = ""
	contexto = {
		'setorselecionado':setor,
		'servidor': servidor,
		'setores': setores,
		'form': form,
		'page_obj': page_obj,
	}

	if request.method == 'POST':
		if form.is_valid():
			setores2 = []
			pattern = re.compile(form.cleaned_data['nome'].upper())
			for setor in setores:
				if pattern.search(setor.nome.upper()):
					setores2.append(setor)
			if setores2:
				page = request.GET.get('page')
				paginator = Paginator(setores2, 15)
				page_obj = paginator.get_page(page)

				contexto = { 
					'setorselecionado':setor,
					'servidor': servidor,
					'setores': setores,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				print('entrei no form invalid')
				messages.warning(request, 'Setor com este nome não encontrado!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_historico(request):
	return render(request, 'admin_historico.html')

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_add_noturno(request, template_name='namp/relatorio/admin_add_noturno.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		setores = Setor.objects.all()
	except Setor.DoesNotExist:
		messages.warning(request, 'Setor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = AddNoturnoForm(request.POST or None)
 
	page = request.GET.get('page')
	paginator = Paginator(list(setores), 15)
	page_obj = paginator.get_page(page)
	setor = None
	
	contexto = {
		'servidor': servidor,
		'setores': setores,
		'form': form,
		'page_obj': page_obj,
	}

	if request.method == 'POST':
		if form.is_valid():
			setores = []
		return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_servidor_list(request,template_name='namp/servidor/admin_servidor_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		servidores = list(Servidor.objects.all())
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	form = ServidorSearchForm(request.POST or None)
	
	page = request.GET.get('page')
	paginator = Paginator(servidores, 15)
	page_obj = paginator.get_page(page)

	contexto = { 
		'servidor': servidor,
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
					'servidor': servidor,
					'servidores': servidores2,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				print('entrei no form invalido')
				messages.warning(request, 'Servidor com este nome não encontrado!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_servidor_criar(request,template_name='namp/servidor/admin_servidor_criar.html'):
	servidor = Servidor.objects.get(fk_user=request.user.id)
	form = ServidorCriarForm()

	if request.method == 'POST':
		form = ServidorCriarForm(request.POST)		
		if form.is_valid():
			form.save()
			messages.success(request, 'Servidor adicionada com suceso!')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			contexto = {
				'form': form,
				'servidor': servidor,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	else:
		contexto = {
			'form': form,
			'servidor': servidor,
		}
	return render(request,template_name)

'''
Acionada pelo botão ADICIONAR, localizado na template de PERÍODOS.
'''
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def periodo_criar(request, template_name="namp/periodo/periodo_criar.html"):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = PeriodoAcaoForm()
	contexto = {
		'form': form,
		'servidor': servidor,
	}
	if request.method == 'POST':
		form = PeriodoAcaoForm(request.POST)		
		if form.is_valid():
			print(form.cleaned_data)
			try:
				PeriodoAcao.objects.get(descricao=form.cleaned_data['descricao'],data_inicial__month=form.cleaned_data['data_inicial'].month,data_final__month=form.cleaned_data['data_final'].month)
			except PeriodoAcao.DoesNotExist:
				form.save()
				messages.success(request, 'Período cadastrado com sucesso!')
				return redirect('namp:periodo_listar')
			else:
				messages.warning(request, 'Ops! Período com a descrição e o intervalo de datas informados já existe!')
				return redirect('namp:periodo_listar')
		else:
			contexto['form'] = form
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	return render(request,template_name, contexto)
'''
Acionada pelo link PERÍODOS, localizado na aba do GESTOR.
'''
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def periodo_listar(request, template_name="namp/periodo/periodo_listar.html"):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		periodos = PeriodoAcao.objects.all()
		setores = list(Setor.objects.all())
		escalasfrequencias = EscalaFrequencia.objects.all().values_list('fk_setor')
	except PeriodoAcao.DoesNotExist:
		messages.warning(request,'Não há períodos registrados até o momento.')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Setor.DoesNotExist:
		messages.warning(request,'Não há setores registrados até o momento.')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	page = request.GET.get('page')
	paginator = Paginator(list(periodos), 15)
	page_obj = paginator.get_page(page)

	form = PeriodoAcaoSearchForm()
	#selecionando os períodos específicos mais recentes
	periodo_escala_atual = periodos.filter(descricao='GERAR ESCALAS',data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	periodo_frequencia_atual = periodos.filter(descricao='CONSOLIDAR FREQUENCIAS',data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	#Definindo as variáveis que levarão à template as unidades que submeteram escalas e frequeências
	if periodo_escala_atual: escalas = [escala for tupla in escalasfrequencias.filter(fk_periodo_acao__descricao='GERAR ESCALAS', data__gte=periodo_escala_atual.data_inicial, data__lte=periodo_escala_atual.data_final) for escala in tupla]
	else: escalas = []
	if periodo_frequencia_atual: frequencias = [frequencia for tupla in escalasfrequencias.filter(fk_periodo_acao__descricao='CONSOLIDAR FREQUENCIAS', data__gte=periodo_frequencia_atual.data_inicial, data__lte=periodo_frequencia_atual.data_final) for frequencia in tupla]
	else: frequencias = []
	contexto = { 
		'form': form,
		'setores':setores,
		'page_obj': page_obj,
		'servidor':servidor,
		'escalas':escalas,
		'frequencias': frequencias,
	}

	if request.method == 'POST':
		form = PeriodoAcaoSearchForm(request.POST)
		if form.is_valid():
			periodos2 = []
			meses = {
			'Jan':'JANEIRO', 
			'Feb':'FEVEREIRO', 
			'Mar':'MARÇO', 
			'Apr':'ABRIL', 
			'May':'MAIO', 
			'Jun':'JUNHO', 
			'Jul':'JULHO', 
			'Aug':'AGOSTO', 
			'Sep':'SETEMBRO', 
			'Oct':'OUTUBRO', 
			'Nov':'NOVEMBRO', 
			'Dec':'DEZEMBRO',
			}
			pattern = re.compile(form.cleaned_data['descricao'].upper())
			for periodo in periodos:
				if periodo.descricao == 'GERAR ESCALAS':
					if pattern.search(periodo.descricao.upper()) or pattern.search(meses[periodo.data_inicial.replace(month=periodo.data_inicial.month+1).strftime('%b')]):
						periodos2.append(periodo)
				else:
					if pattern.search(periodo.descricao.upper()) or pattern.search(meses[periodo.data_inicial.replace(month=periodo.data_inicial.month-1).strftime('%b')]):
						periodos2.append(periodo)
			if periodos2:
				page = request.GET.get('page')
				paginator = Paginator(periodos2, 15)
				page_obj = paginator.get_page(page)
				
				contexto = { 
					'form': form,
					'setores':setores,
					'page_obj': page_obj,
					'servidor':servidor,
					'escalas':escalas,
					'frequencias': frequencias,
				}
				return render(request, template_name, contexto)
			else:
				messages.warning(request, 'Período ou evento não encontrado!')
				return render(request, template_name, contexto)
	print(escalas)
	print(frequencias)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def periodo_att(request, id_periodo_acao):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		periodo = PeriodoAcao.objects.get(id_periodo_acao=id_periodo_acao)
	except PeriodoAcao.DoesNotExist:
		messages.warning(request, 'Período ou evento não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	form = PeriodoAcaoForm(instance=periodo)
	form.fields['descricao'].choices = [(periodo.descricao,periodo.descricao)]
	contexto = {
			'form': form,
			'id_periodo_acao':id_periodo_acao,
			'servidor':servidor,
		}
	if request.method == 'POST':
		form = PeriodoAcaoForm(request.POST,instance=periodo)
		if form.is_valid():
			form.save()
			messages.success(request, 'Período editado com suceso!')
			return redirect('namp:periodo_listar')
		else:
			contexto['form']=form
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/periodo/periodo_att.html',contexto)
	return render(request, 'namp/periodo/periodo_att.html',contexto)


#SETOR
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def setor_att(request, id_setor):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		setor = Setor.objects.get(id_setor=id_setor)
		enderecosetor = EnderecoSetor.objects.get(fk_setor=setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except EnderecoSetor.DoesNotExist:
		enderecosetor = None
	except Setor.DoesNotExist:
		messages.warning(request, 'Não foi possível carregar o setor!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	if servidor.fk_setor == setor or request.user.is_superuser:
		'''
		Atribuindo o formulário do setor a uma variável e setando alguns campos choices para inicialização.
		'''
		enderecosetorform = EnderecoSetorForm(instance=enderecosetor)
		enderecosetorform.fields['fk_setor'].choices = list(Setor.objects.filter(id_setor=setor.id_setor).values_list('id_setor', 'nome'))

		contexto = {
			'servidor':servidor,
			'setorform': SetorForm(instance=setor),
			'enderecosetorform': enderecosetorform,
		}

		if request.method == 'POST':
			contexto['setorform'] = SetorForm(request.POST, instance=setor)
			contexto['enderecosetorform'] = EnderecoSetorForm(request.POST, instance=enderecosetor)

			if contexto['setorform'].is_valid():
				setorform = contexto['setorform'].save(commit=False)
				if contexto['enderecosetorform'].is_valid():
					enderecoform = contexto['enderecosetorform'].save(commit=False)
					setorform.save()
					enderecoform.save()
					messages.success(request, 'Setor editado com suceso!')
					return HttpResponseRedirect('/')
				else:
					contexto['setorform'] = SetorForm(request.POST, instance=setor)
					contexto['enderecosetorform'] = EnderecoSetorForm(request.POST)
					
					messages.warning(request, 'Erro no formulário do endereço')
					return render(request, 'namp/setor/setor_att.html',contexto)
			else:
				contexto['setorform'] = SetorForm(request.POST, instance=setor)
				contexto['enderecosetorform'] = EnderecoSetorForm(request.POST)

				messages.warning(request, 'Erro no formulário do setor')
				return render(request, 'namp/setor/setor_att.html',contexto)
		return render(request, 'namp/setor/setor_att.html',contexto)
	messages.error(request, 'Acesso negado! Entre como Administrador para continuar.')	
	return redirect('autenticacao:login')

#Esta view foi revisada em 14/07 e está funcional
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_criar(request, template_name='namp/equipe/equipe_criar.html'):
	servidor = Servidor.objects.get(fk_user=request.user.id)
	form = EquipeForm()
	try:
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
		form.fields['fk_setor'].choices = list(Setor.objects.filter(id_setor=setor.id_setor).values_list('id_setor', 'nome'))
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if request.method == 'POST':
		form = EquipeForm(request.POST)		
		if form.is_valid():
			form.save()
			messages.success(request, 'Equipe adicionada com suceso!')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			contexto = {
				'setor': setor,
				'form': form,
				'servidor': servidor,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	else:
		contexto = {
			'setor': setor,
			'form': form,
			'servidor': servidor,
		}
		return render(request,template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_list(request, template_name='namp/equipe/equipe_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		servidores = Servidor.objects.filter(fk_setor=servidor.fk_setor)
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
		'servidores':servidores, 
		'servidor': servidor,
		'form': form,
		'page_obj': page_obj,
	}
	if request.method == 'POST':
		if form.is_valid():
			equipes2 = []
			pattern = re.compile(form.cleaned_data['nome'].upper())
			for equipe in equipes:
				if pattern.search(equipe.nome.upper()):
					equipes2.append(equipe)
			if equipes2:
				page = request.GET.get('page')
				paginator = Paginator(equipes2, 15)
				page_obj = paginator.get_page(page)
				contexto['page_obj']= page_obj
				return render(request, template_name, contexto)
			else:
				messages.warning(request, 'Equipe com este nome não encontrada!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_att(request, id_equipe):
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
			form.save()
			messages.success(request, 'Equipe editada com suceso!')
			return HttpResponseRedirect('/equipes')
		else:
			contexto = {
				'equipe':equipe,
				'servidor': servidor,
				'form': form
			}
			#messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			messages.warning(request,form.errors.get_json_data(escape_html=False))
			return render(request, 'namp/equipe/equipe_att.html',contexto)
	else:
		contexto = {
			'equipe':equipe,
			'servidor': servidor,
			'form': form
		}
		return render(request, 'namp/equipe/equipe_att.html',contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def equipe_delete(request, id_equipe):
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
	return HttpResponseRedirect("/")
	
from django.views.generic import ListView
class EquipeServidores(ListView):
	def get(self,request):
		try:
			equipe = Equipe.objects.get(id_equipe=self)
		except Equipe.DoesNotExist:
			equipe = None
		contexto = {
			'equipe': equipe,
		}
		return render(request, 'includes/modal/equipe/equipe_servidores.html', contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def servidor_mov(request, template_name='namp/servidor/servidor_mov.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		setor = Servidor.objects.get(fk_user=request.user.id).fk_setor
		servidores = Servidor.objects.filter(fk_setor=setor)
		equipes = Equipe.objects.filter(fk_setor=setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Equipe.DoesNotExist:
		messages.warning(request, 'Não há equipes cadastradas para esse setor!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = ServidorMoverIntForm()
	form.fields['servidor'].choices = [('', '--Selecione--')] + list(servidores.values_list('id_matricula','nome'))
	form.fields['equipe_origem'].choices = [('', '--Selecione--')]
	form.fields['equipe_destino'].choices = [('', '--Selecione--')] + list(equipes.values_list('id_equipe','nome'))
	contexto = {
		'setor':setor,
		'form': form,
		'servidor': servidor,
	}
	if request.method == 'POST':
		form = ServidorMoverIntForm(request.POST)
		if form.is_valid():
			try:
				servidor = Servidor.objects.get(id_matricula=form.cleaned_data['servidor'])
				equipe = Equipe.objects.get(id_equipe=form.cleaned_data['equipe_destino'])
			except Servidor.DoesNotExist:
				messages.warning(request, 'Servidor não encontrado!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
			except Equipe.DoesNotExist:
				messages.warning(request, 'Equipe não encontrado!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))			
			
			servidor.fk_equipe = equipe
			servidor.save()
			messages.success(request, 'Movimentação realizada com suceso!')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
			#return HttpResponseRedirect(request.META.get('HTTP_REFERER'))	
		else:
			contexto = {
				'setor':setor,
				'form': form,
				'servidor': servidor,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name,contexto)
	return render(request, template_name,contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def admin_servidor_mov(request, template_name='namp/servidor/admin_servidor_mov.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = ServidorMoverExtForm()
	
	contexto = {
		'form': form,
		'servidor': servidor,
	}
	if request.method == 'POST':
		form = ServidorMoverExtForm(request.POST)
		if form.is_valid():
			try:
				servidor = Servidor.objects.get(id_matricula=form.cleaned_data['servidor'])
				setor = Setor.objects.get(id_setor=form.cleaned_data['setor_destino'])
				equipe = Equipe.objects.get(fk_setor=setor,id_equipe=form.cleaned_data['equipe_destino'])
			except Servidor.DoesNotExist:
				messages.warning(request, 'Servidor não encontrado!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
			except Setor.DoesNotExist:
				messages.warning(request, 'Setor não encontrado!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))			
			except Equipe.DoesNotExist:
				messages.warning(request, 'Equipe não encontrada!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))			
			else:
				servidor.fk_setor = setor
				servidor.fk_equipe = equipe
				servidor.save()
				messages.success(request, 'Movimentação realizada com suceso!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			contexto['form'] = form
			messages.warning(request,'Algo de errado aconteceu!')
			#messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name,contexto)
	return render(request, template_name,contexto)


@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def servidor_list(request,template_name='namp/servidor/servidor_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except Equipe.DoesNotExist:
		messages.warning(request, 'Unidade não possui equipes cadastradas')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	form = ServidorSearchForm(request.POST or None)
	
	servidores = list(Servidor.objects.filter(fk_equipe__fk_setor=servidor.fk_setor))

	page = request.GET.get('page')
	paginator = Paginator(servidores, 15)
	page_obj = paginator.get_page(page)

	contexto = { 
		'servidor': servidor,
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
					'servidor': servidor,
					'form': form,
					'page_obj': page_obj,
				}
				return render(request, template_name, contexto)
			else:
				messages.warning(request, 'Servidor com este nome não encontrado!')
				return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def escala_operador_list(request,template_name='namp/escala/escala_operador_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		escalas = EscalaFrequencia.objects.filter(fk_setor=servidor.fk_setor).filter(fk_periodo_acao__descricao='GERAR ESCALAS')
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	meses = {
		'Jan':'JANEIRO', 
		'Feb':'FEVEREIRO', 
		'Mar':'MARÇO', 
		'Apr':'ABRIL', 
		'May':'MAIO', 
		'Jun':'JUNHO', 
		'Jul':'JULHO', 
		'Aug':'AGOSTO', 
		'Sep':'SETEMBRO', 
		'Oct':'OUTUBRO', 
		'Nov':'NOVEMBRO', 
		'Dec':'DEZEMBRO',
	}

	page = request.GET.get('page')
	paginator = Paginator(list(escalas), 15)
	page_obj = paginator.get_page(page)

	mensagens = {}

	#Verificando se tem período aberto para gerar escalas
	periodo_escala = PeriodoAcao.objects.filter(descricao='GERAR ESCALAS', data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()

	if periodo_escala:
		escalas_geradas = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_escala, fk_setor=servidor.fk_setor)
		if not escalas_geradas:
			mensagens['mensagem_escalas'] = 'O período para gerar as escalas do seu setor para o mês de ' + meses[periodo_escala.data_inicial.replace(month=periodo_escala.data_inicial.month+1).strftime('%b')] + ' encontra-se aberto até ' + periodo_escala.data_final.strftime('%d/%m/%Y %H:%M') + '. Clique no botão GERAR ESCALAS.'
	
	form = EscalaFrequenciaSearchForm(request.POST or None)
	
	contexto = { 
		'servidor': servidor,
		'mensagens': mensagens,
		'page_obj': page_obj,
		'form': form,
	}

	if request.method == 'POST':
		if form.is_valid():
			escalas2 = []
			
		pattern = re.compile(form.cleaned_data['mes'].upper())
		for escala in escalas:
			if pattern.search(meses[escala.data.replace(month=escala.data.month+1).strftime('%b')]):
				escalas2.append(escala)
			
		if escalas2:
			page = request.GET.get('page')
			paginator = Paginator(escalas2, 15)
			page_obj = paginator.get_page(page)
			contexto['page_obj']=  page_obj
			return render(request, template_name, contexto)
		else:
			messages.warning(request, 'Ops! Setor sem escalas para mês informado.')
			return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def frequencias_operador(request,template_name='namp/frequencia/frequencia_operador_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		periodo_frequencia = PeriodoAcao.objects.filter(descricao='CONSOLIDAR FREQUENCIAS', data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
		escala_gerada = EscalaFrequencia.objects.filter(fk_setor=servidor.fk_setor,data__month=periodo_frequencia.data_final.month-2)
		frequencia_consolidada = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_frequencia, fk_setor=servidor.fk_setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	if periodo_frequencia:
		if escala_gerada:
			if not frequencia_consolidada:
				#realiza a consolidação da frequência
				frequencia = EscalaFrequencia()
				frequencia.fk_periodo_acao = periodo_frequencia
				frequencia.data = DateTime.today()
				frequencia.fk_servidor = servidor
				frequencia.fk_setor = servidor.fk_setor
				frequencia.save()
				messages.success(request, 'Frequência consolidada!')
				return HttpResponseRedirect('/frequencia_operador_list')
			else:
				messages.warning(request, 'As frequências do período atual já foram consolidadas!')
				return HttpResponseRedirect('/frequencia_operador_list')
		else:
			messages.warning(request, 'Setor sem escalas geradas para o período de consolidação atual!')
			return HttpResponseRedirect('/frequencia_operador_list')
	messages.warning(request, 'Período de consolidação de frequências indisponível!')
	return HttpResponseRedirect('/frequencia_operador_list')

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def frequencia_operador_list(request,template_name='namp/frequencia/frequencia_operador_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		frequencias = EscalaFrequencia.objects.filter(fk_setor=servidor.fk_setor, fk_periodo_acao__descricao='CONSOLIDAR FREQUENCIAS')
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	meses = {
	'Jan':'JANEIRO', 
	'Feb':'FEVEREIRO', 
	'Mar':'MARÇO', 
	'Apr':'ABRIL', 
	'May':'MAIO', 
	'Jun':'JUNHO', 
	'Jul':'JULHO', 
	'Aug':'AGOSTO', 
	'Sep':'SETEMBRO', 
	'Oct':'OUTUBRO', 
	'Nov':'NOVEMBRO', 
	'Dec':'DEZEMBRO',
	}

	page = request.GET.get('page')
	paginator = Paginator(list(frequencias), 15)
	page_obj = paginator.get_page(page)

	mensagens = {}
				
	#Verificando se tem período aberto para consolidar frequências
	periodo_frequencia = PeriodoAcao.objects.filter(descricao='CONSOLIDAR FREQUENCIAS', data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()

	if periodo_frequencia:
		frequencia_gerada = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_frequencia, fk_setor=servidor.fk_setor)
		if not frequencia_gerada:
			mensagens['mensagem_frequencia'] = 'O período para consolidar as frequências do seu setor, referentes ao mês de ' + meses[periodo_frequencia.data_inicial.replace(month=periodo_frequencia.data_inicial.month-1).strftime('%b')] + ', encontra-se aberto até ' + periodo_frequencia.data_final.strftime('%d/%m/%Y %H:%M') + '. Clique no botão CONSOLIDAR.'	
	
	form = EscalaFrequenciaSearchForm(request.POST or None)
	
	contexto = { 
		'servidor': servidor,
		'mensagens': mensagens,
		'page_obj': page_obj,
		'form': form,
	}

	if request.method == 'POST':
		if form.is_valid():
			frequencias2 = []
			
		pattern = re.compile(form.cleaned_data['mes'].upper())
		for frequencia in frequencias:
			if pattern.search(meses[frequencia.data.replace(month=frequencia.data.month-1).strftime('%b')]):
				frequencias2.append(frequencia)
			
		if frequencias2:
			page = request.GET.get('page')
			paginator = Paginator(frequencias2, 15)
			page_obj = paginator.get_page(page)
			contexto['page_obj'] =  page_obj
			return render(request, template_name, contexto)
		else:
			messages.warning(request, 'Ops! Setor sem frequências para mês informado.')
			return render(request, template_name, contexto)
	return render(request, template_name, contexto)

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_criar(request,template_name='namp/afastamento/afastamento_criar.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
	
	form = AfastamentoForm()
	form.fields['fk_servidor'].choices = [('', '---------')] + list(Servidor.objects.filter(fk_setor=servidor.fk_setor).values_list('id_matricula', 'nome'))
	contexto = { 
		'servidor': servidor,
		'form': form
	}
	if request.method == 'POST':
		form = AfastamentoForm(request.POST)
		if form.is_valid():
			afastamento = form.save(commit=False)
			for afastam in list(HistAfastamento.objects.filter(fk_servidor=afastamento.fk_servidor, data_inicial__month=afastamento.data_inicial.month, data_final__month=afastamento.data_final.month)):
				if afastamento.data_inicial >= afastam.data_inicial or afastamento.data_final <= afastam.data_final:
					messages.warning(request, 'O servidor já possui um afasamento nesse intervalo de datas!')	
					contexto['form'] = form
					return render(request, template_name, contexto)
			afastamento.save()
			messages.success(request, 'Afastamento cadastrado com sucesso!')	
			return redirect('namp:afastamento_list')
		else:
			contexto['form'] = form
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, template_name, contexto)
	return render(request, template_name, contexto)

#SERVIDOR
@login_required(login_url='/autenticacao/login/')
def servidor_att(request, id_matricula):

	try:
		user = Servidor.objects.get(fk_user=request.user.id)
		servidor = Servidor.objects.get(id_matricula=id_matricula)
		enderecoservidor = EnderecoServ.objects.get(fk_servidor=servidor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except EnderecoServ.DoesNotExist:
		enderecoservidor = None
	
	if request.user == servidor.fk_user or request.user.is_staff:
		enderecoservform = EnderecoServForm(instance=enderecoservidor)
		enderecoservform.fields['fk_servidor'].choices = list(Servidor.objects.filter(id_matricula=servidor.id_matricula).values_list('id_matricula', 'nome'))

		contexto = {
			'user': user,
			'servidor':servidor,
			'servidorform': ServidorForm(instance=servidor),
			'enderecoservform': enderecoservform,
		}

		if not request.user.is_superuser:
			if servidor.sexo == 'M': contexto['servidorform'].fields['sexo'].choices = [(servidor.sexo,'Masculino')]
			else: contexto['servidorform'].fields['sexo'].choices = [(servidor.sexo,'Feminino')]
			contexto['servidorform'].fields['cargo'].choices = [(servidor.cargo,servidor.cargo)]
			contexto['servidorform'].fields['cf'].choices = [(servidor.cf,servidor.cf)]
			contexto['servidorform'].fields['tipo_vinculo'].choices = [(servidor.tipo_vinculo,servidor.tipo_vinculo)]
			contexto['servidorform'].fields['regime_juridico'].choices = [(servidor.regime_juridico,servidor.regime_juridico)]
			contexto['servidorform'].fields['fk_setor'].choices = [(servidor.fk_setor.id_setor,servidor.fk_setor.nome)]
			contexto['servidorform'].fields['fk_equipe'].choices = [(servidor.fk_equipe.id_equipe,servidor.fk_equipe.nome)]

		if request.method == 'POST':
			contexto['servidorform'] = ServidorForm(request.POST, instance=servidor)
			contexto['enderecoservform'] = EnderecoServForm(request.POST, instance=enderecoservidor) or None
			if contexto['servidorform'].is_valid():
				servidor = contexto['servidorform'].save(commit=False)
				if contexto['enderecoservform'].is_valid():
					endereco = contexto['enderecoservform'].save(commit=False)
					servidor.save()
					endereco.save()
					messages.success(request, 'Servidor editado com suceso!')
					return HttpResponseRedirect('/')
				else:
					contexto['servidorform'] = ServidorForm(request.POST, instance=servidor)
					contexto['enderecoservform'] = EnderecoServForm(request.POST) or None
					
					messages.warning(request, 'Erro no formulário do endereço')
					return render(request, 'namp/servidor/servidor_att.html',contexto)
			else:
				contexto['servidorform'] = ServidorForm(request.POST, instance=servidor)
				contexto['enderecoservform'] = EnderecoServForm(request.POST) or None

			messages.warning(request, 'Erro no formulário do servidor')
			return render(request, 'namp/servidor/servidor_att.html',contexto)
		return render(request, 'namp/servidor/servidor_att.html',contexto)
	return redirect('autenticacao:login')
def servidor_escala(request):
	return render(request, 'servidor_escala.html')

def servidor_hist(request):
	return render(request, 'servidor_hist.html')

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
def frequencias_admin_list(request,template_name='namp/frequencia/frequencias_admin_list.html'):
	print('Acesso view de frequencias_admin!')
	return render(request,template_name, {})

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def add_noturno_list(request,template_name='namp/jornada/add_noturno_list.html'):
	print('entrei em LISTA DE ADD NOTURNO')
	return render(request,template_name, {})

@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_list(request, template_name='namp/afastamento/afastamento_list.html'):
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
'''
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
'''
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def afastamento_att_form(request, id_hist_afastamento):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		afastamento = HistAfastamento.objects.get(id_hist_afastamento=id_hist_afastamento)
	except HistAfastamento.DoesNotExist:
		messages.warning(request, 'Afastamento não encontrado!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	servidores = list(Servidor.objects.filter(fk_setor=servidor.fk_setor).values_list('id_matricula', 'nome'))
	form = AfastamentoForm(instance=afastamento)

	if request.method == 'POST':
		form = AfastamentoForm(request.POST, instance=afastamento)
		if form.is_valid():
			form.save()
			messages.success(request, 'Afastamento editado com suceso!')
			return HttpResponseRedirect('/afastamento_change_list')
		else:
			contexto = {
				'servidor': servidor,
				'form': form,
				'afastamento': afastamento,
			}
			messages.warning(request, form.errors.get_json_data(escape_html=False)['__all__'][0]['message'])
			return render(request, 'namp/afastamento/afastamento_att_form.html',contexto)
	else:
		contexto = {
			'servidor':servidor,
			'form': form,
			'afastamento': afastamento,
		}
		return render(request, 'namp/afastamento/afastamento_att_form.html',contexto)

'''
@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def escalas_operador_list(request,template_name='namp/escala/escalas_operador_list.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		escalas = EscalaFrequencia.objects.filter(fk_setor=servidor.fk_setor, fk_periodo_acao__descricao=1)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	#form = EscalaFrequenciaSearchForm(request.POST or None)
	
	page = request.GET.get('page')
	paginator = Paginator(list(escalas), 15)
	page_obj = paginator.get_page(page)
	mensagens = {}
				
	#Verificando se tem período para consolidar escalas
	periodo_escala = PeriodoAcao.objects.filter(descricao=1, data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	periodo_frequencia = PeriodoAcao.objects.filter(descricao=2, data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today()).order_by('-data_inicial').first()
	if periodo_escala:
		escalas_geradas = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_escala)
		if not escalas_geradas:
			mensagens['mensagem_escalas'] = 'O período para consolidar as escalas do mês de ' + periodo_escala.data_inicial.strftime('%B') + ' encontra-se em aberto até ' + periodo_escala.data_final.strftime('%d/%m/%Y %H:%M')
	if periodo_frequencia:
		frequencia_gerada = EscalaFrequencia.objects.filter(fk_periodo_acao=periodo_frequencia)
		if not frequencia_gerada:
			mensagens['mensagem_frequencia'] = 'O período para consolidar as frequências do mês de ' + (periodo_frequencia.data_inicial - TimeDelta(days=30)).strftime('%B') + ' encontra-se em aberto até ' + periodo_frequencia.data_final.strftime('%d/%m/%Y %H:%M')		
			
	contexto = { 
		'servidor': servidor,
		'mensagens': mensagens,
		'page_obj': page_obj,
	}
	return render(request, template_name, contexto)'''


@login_required(login_url='/autenticacao/login/')
@staff_member_required(login_url='/autenticacao/login/')
def jornadas_operador(request,template_name='namp/jornada/jornadas_operador.html'):
	try:
		servidor = Servidor.objects.get(fk_user=request.user.id)
		periodo_escala = PeriodoAcao.objects.get(descricao='GERAR ESCALAS', data_inicial__lte=DateTime.today(), data_final__gte=DateTime.today())
		escala_gerada = EscalaFrequencia.objects.get(fk_periodo_acao=periodo_escala, fk_setor=servidor.fk_setor)
	except Servidor.DoesNotExist:
		messages.warning(request, 'Servidor não encontrado para este usuário!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except PeriodoAcao.DoesNotExist:
		#Quando não encontrado o período de gerar escala na data de acesso da template jornadas_operador, 
		#uma mensagem de warning é retornada junto com a template de listar escalas da unidade.
		periodo_escala = None
		messages.warning(request, 'O prazo para gerar escala regular está encerrado!')
		return redirect('namp:escala_operador_list')
	except EscalaFrequencia.DoesNotExist:
		#Quando não encontrada escala regular para o período atual 
		escala_gerada = None
		
	if escala_gerada:
		messages.warning(request, 'Seu setor já possui escala regular para o período atual!')
		return redirect('namp:escala_operador_list')

	equipes = Equipe.objects.filter(status=True).filter(fk_setor=servidor.fk_setor)

	tem_plantao12 = tem_plantao24 = tem_plantao48 = False

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
	
	form = GerarJornadaRegularForm(request.POST or None)
	form.fields['equipe_plantao12h'].choices = [('', '--Selecione--')] + list(equipes.filter(fk_tipo_jornada__carga_horaria=12).values_list('id_equipe', 'nome'))
	form.fields['equipe_plantao24h'].choices = [('', '--Selecione--')] + list(equipes.filter(fk_tipo_jornada__carga_horaria=24).values_list('id_equipe', 'nome'))
	form.fields['equipe_plantao48h'].choices = [('', '--Selecione--')] + list(equipes.filter(fk_tipo_jornada__carga_horaria=48).values_list('id_equipe', 'nome'))

	if not tem_plantao12:
		del form.fields['data_plantao12h']#.widget.attrs['required'] = tem_plantao12
		del form.fields['equipe_plantao12h']#.widget.attrs['required'] = tem_plantao12
	if not tem_plantao24:
		del form.fields['data_plantao24h']#.widget.attrs['required'] = tem_plantao24
		del form.fields['equipe_plantao24h']#.widget.attrs['required'] = tem_plantao24
	if not tem_plantao48:
		del form.fields['data_plantao48h']#.widget.attrs['required'] = tem_plantao48
		del form.fields['equipe_plantao48h']#.widget.attrs['required'] = tem_plantao48

	contexto = {
		'form':form,
		'equipes':equipes,
		'servidor':servidor,
		'tem_plantao12': tem_plantao12,
		'tem_plantao24': tem_plantao24,
		'tem_plantao48': tem_plantao48,
	}
	if request.method=='POST':
		print('formulário preenchido')
		#form = GerarJornadaRegularForm(request.POST)
		if form.is_valid():
			print('formulário validado')
			'''
			Trecho onde se captura a equipe de 12h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''

			if tem_plantao12:
				if form.cleaned_data['equipe_plantao12h'] != '' and form.cleaned_data['data_plantao12h'] is not None and form.cleaned_data['data_plantao12h'].month==periodo_escala.data_inicial.month+1:
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
				else:			
					contexto['form'] = form
					messages.warning(request, 'Ops! A data de início da equipe de 12h está fora do período válido!')
					return render(request, template_name, contexto)
			'''
			Trecho onde se captura a equipe de 24h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''
			if tem_plantao24:
				if form.cleaned_data['equipe_plantao24h'] != '' and form.cleaned_data['data_plantao24h'] is not None:
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
				else:			
					contexto['form'] = form
					messages.warning(request, 'Ops! A data de início da equipe de 24h está fora do período válido!')
					return render(request, template_name, contexto)
			'''--------------------------------------------------------
			Trecho onde se captura a equipe de 48h do formulário,
			a data inicial para essa mesma equipe e todas as equipes
			com tipos de jornada similares.
			'''
			if tem_plantao48:
				if form.cleaned_data['equipe_plantao48h'] != '' and form.cleaned_data['data_plantao48h'] is not None:
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
				else:			
					contexto['form'] = form
					messages.warning(request, 'Ops! A data de início da equipe de 48h está fora do período válido!')
					return render(request, template_name, contexto)

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
			
			escala = EscalaFrequencia()
			escala.fk_periodo_acao = periodo_escala
			escala.data = DateTime.today()
			escala.fk_servidor = servidor
			escala.fk_setor = servidor.fk_setor
			escala.save()

			messages.success(request, 'As escalas foram atualizadas com sucesso!')
			return redirect('namp:escala_operador_list')
		else:
			print('formulário inválido')
			contexto['form'] = form
			messages.warning(request, 'Ops! Verifique os campos do formulário!')
			return render(request, template_name, contexto)
	print('formulário novo')
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
		result = list(Equipe.objects.filter(id_equipe=Servidor.objects.get(id_matricula=id_matricula).fk_equipe.id_equipe).values('id_equipe', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_setor_servidor(request):
	result = list(Setor.objects.none())
	id_matricula = request.GET.get('id_matricula', '')
	if (id_matricula):
		result = list(Setor.objects.filter(id_setor=Servidor.objects.get(id_matricula=id_matricula).fk_setor.id_setor).values('id_setor', 'nome'))
	return HttpResponse(json.dumps(result), content_type="application/json")

def get_add_noturno(request):
	print("entrei na função")
	result = list(Setor.objects.none())
	id_matricula = request.GET.get('id_matricula', '')
	print("vou encontrar o servidor")
	if (id_matricula):
		result = list(Setor.objects.filter(id_setor=Servidor.objects.get(id_matricula=id_matricula).fk_setor.id_setor).values('id_setor', 'nome'))
		print("encontrei")
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
	print('Fui chamada para gerar as escalas')
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
	servidores = list(Servidor.objects.all())

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

		#if servidores.tipo_vinculo == 'Concursado':
		if servidores.values_list('tipo_vinculo') == 'Concursado':
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