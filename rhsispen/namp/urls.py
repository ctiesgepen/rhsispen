# coding=utf-8
from namp.views import *
from . import views
from django.conf.urls import  url
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'namp'

urlpatterns = [
	path('', views.home, name='home'),
	#Tela do Operador
	path('equipe_operador_change_form/', views.equipe_operador_change_form, name='equipe_operador_change_form'),
	path('equipe_operador_change_list/', views.equipe_operador_change_list, name='equipe_operador_change_list'),
	path('equipe_operador_att_form/<int:id_equipe>/', views.equipe_operador_att_form, name='equipe_operador_att_form'),
	path('equipe_delete/<int:id_equipe>/delete', views.EquipeDeleteView, name='equipe_delete'),
	
	path('servidores_operador_change_list/', views.servidores_operador_change_list, name='servidores_operador_change_list'),
	path('servidor_operador_change_form/<int:id_matricula>/', views.servidor_operador_change_form, name='servidor_operador_change_form'),
	path('servidor_operador_att_form/<int:id_matricula>/', views.servidor_operador_att_form, name='servidor_operador_att_form'),
	
	path('afastamento_change_form/', views.afastamento_change_form, name='afastamento_change_form'),
	path('afastamento_change_list/', views.afastamento_change_list, name='afastamento_change_list'),
	path('afastamento_att_form/<int:id_hist_afastamento>/', views.afastamento_att_form, name='afastamento_att_form'),

	path('jornadas_operador/', views.jornadas_operador, name='jornadas_operador'),

	path('escalas_operador_list/', views.escalas_operador_list, name='escalas_operador_list'),
	
	path('frequencias_operador_list/', views.frequencias_operador_list, name='frequencias_operador_list'),

	path('add_noturno_list', views.add_noturno_list, name='add_noturno_list'),
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
