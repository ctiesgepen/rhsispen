# coding=utf-8
from namp.views import *
from . import views
from django.conf.urls import  url
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'namp'

urlpatterns = [
	path('', views.home, name='home'),

	#Tela do GESTOR
	path('admin_afastamento/', views.admin_afastamento, name='admin_afastamento'),
	path('admin_servidor/', views.admin_servidor, name='admin_servidor'), #falta fazer
	path('admin_setores/', views.admin_setores, name='admin_setores'), #falta fazer
	path('admin_unidades/', views.admin_unidades, name='admin_unidades'), 
	path('admin_historico/', views.admin_unidades, name='admin_historico'), #falta fazer
	path('admin_add_noturno/', views.admin_add_noturno, name='admin_add_noturno'), #falta fazer
	path('admin_servidores/', views.admin_servidores, name='admin_servidores'), #falta fazer
	path('admin_escalas_frequencias/', views.admin_escalas_frequencias, name='admin_escalas_frequencias'),#falta fazer

	#Tela do OPERADOR
	path('equipes/<int:id_equipe>/editar/', views.equipe_att, name='equipe_att'),
	path('equipes/cadastrar/', views.equipe_criar, name='equipe_criar'),
	path('equipes/', views.equipe_list, name='equipe_list'),
	path('equipe_delete/<int:id_equipe>/delete', views.equipe_delete, name='equipe_delete'),
	path('servidor_mov/', views.servidor_mov, name='servidor_mov'), #falta fazer
	path('servidor_list/', views.servidor_list, name='servidor_list'), #falta fazer
	path('escala_operador_list/', views.escala_operador_list, name='escala_operador_list'),
	path('jornadas_operador/', views.jornadas_operador, name='jornadas_operador'),
	path('frequencia_operador_list/', views.frequencia_operador_list, name='frequencia_operador_list'),
	path('operador_afastamentos/', views.operador_afastamentos, name='operador_afastamentos'), 	

	#Tela do SERVIDOR
	path('servidor_att/<int:id_matricula>/', views.servidor_att, name='servidor_att'),
	path('servidor_escala/', views.servidor_escala, name='servidor_escala'), #falta fazer
	path('servidor_hist/', views.servidor_hist, name='servidor_hist'), #falta fazer


	#path('equipe_operador_change_form/', views.equipe_operador_change_form, name='equipe_operador_change_form'),
	#path('equipe_operador_change_list/', views.equipe_operador_change_list, name='equipe_operador_change_list'),
	#path('equipe_operador_att_form/<int:id_equipe>/', views.equipe_operador_att_form, name='equipe_operador_att_form'),
	#path('equipe_delete/<int:id_equipe>/delete', views.EquipeDeleteView, name='equipe_delete'),
	
	#path('servidores_operador_change_list/', views.servidores_operador_change_list, name='servidores_operador_change_list'),
	#path('servidor_operador_change_form/<int:id_matricula>/', views.servidor_operador_change_form, name='servidor_operador_change_form'),
	#path('servidor_operador_att_form/<int:id_matricula>/', views.servidor_operador_att_form, name='servidor_operador_att_form'),
	
	#path('afastamento_change_form/', views.afastamento_change_form, name='afastamento_change_form'),
	#path('afastamento_change_list/', views.afastamento_change_list, name='afastamento_change_list'),
	#path('afastamento_att_form/<int:id_hist_afastamento>/', views.afastamento_att_form, name='afastamento_att_form'),

	#path('jornadas_operador/', views.jornadas_operador, name='jornadas_operador'),

	#path('escalas_operador_list/', views.escalas_operador_list, name='escalas_operador_list'),
	
	#path('frequencias_operador_list/', views.frequencias_operador_list, name='frequencias_operador_list'),
	#path('frequencias_admin_list/', views.frequencias_admin_list, name='frequencias_admin_list'),

	#path('add_noturno_list', views.add_noturno_list, name='add_noturno_list'),

	#Calculos
	url('getEquipes/$', views.get_equipes),
	url('getEquipes24h/$', views.get_equipes24h),
	url('getEquipes48h/$', views.get_equipes48h),
	url('getTipoJornada/', views.get_tipo_jornada),
	url('getEquipeServidor/$', views.get_equipe_servidor),
	url('escala-regular/', views.definirjornadaregular, name='definirjornadaregular'),
	url('gerarescalaregular/', views.gerarescalaregular, name='gerarescalaregular'),
	#Exportações
	url('exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),
	#botões para documentos
	url(r'^frequencia-excel/xls/$', views.exportar_frequencia_excel, name='exportar_frequencia_excel'),
	url(r'^jornadas-excel/xls/$', views.exportar_jornadas_excel, name='exportar_jornadas_excel'),
	url(r'^adicional-noturno/xls/$', views.exportar_noturno_excel, name='exportar_noturno_excel'),	
]
