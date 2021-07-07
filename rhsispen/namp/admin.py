# Register your models here.
from django.core import serializers
import json
from django import forms 
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.serializers.json import DjangoJSONEncoder
from namp.models import Afastamento, ContatoEquipe, EnderecoServ, EnderecoSetor, Equipe, Funcao, HistAfastamento, HistFuncao, HistLotacao, HistStatusFuncional, Jornada, Regiao, Servidor, Setor, StatusFuncional, TipoJornada, Escala
from namp.forms import *

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count
from django.core.exceptions import ValidationError
from datetime import timedelta as TimeDelta, datetime as DateTime, date as Date
# Register your models here.

admin.site.site_header = 'Núcleo de Apoio e Movimentação de Pessoal'
admin.site.login_template = 'autenticacao/login.html'

class OperadorAdminSite(admin.AdminSite):
    pass
operador_admin_site = OperadorAdminSite(name='operador_admin')
operador_admin_site.register(Equipe)
operador_admin_site.register(Group)
operador_admin_site.register(User)

@admin.register(Afastamento)
class AfastamentoAdmin(admin.ModelAdmin):
	list_display = ('codigo_afastamento','tipificacao','descricao')
	#inlines = [descricaoInline]

class ContatoEquipeInline(admin.TabularInline):
    model = ContatoEquipe
    extra = 0

#class ContatoServInline(admin.TabularInline):
#    model = ContatoServ
#    extra = 0

class EnderecoServInline(admin.StackedInline):
	model=EnderecoServ
	fieldsets = (
		(None, {
			'fields': (('uf', 'municipio'), 'cep', ('endereco', 'bairro'), ('numero', 'complemento'))
	            }),
	)

class ServidorInline(admin.TabularInline):
	model=Servidor
	fields = ('nome', 'id_matricula','cpf', 'cargo')
	#readonly_fields = ('nome', 'id_matricula','cpf', 'cargo')

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
	list_display = ('nome', 'fk_setor', 'status','hora_inicial','categoria', 'get_servidor')
	list_filter = ('categoria',)
	search_fields = ['nome', 'fk_setor__nome']
	autocomplete_fields = ['fk_setor']
	list_per_page = 10
	readonly_fields = ('deleted_on',)
	inlines=[ContatoEquipeInline, ServidorInline]
	
	def get_servidor(self, obj):
		return Servidor.objects.filter(fk_equipe=obj).count()
	get_servidor.short_description = 'Servidores'  #Renames column head
	get_servidor.admin_order_field = 'nome'

class EquipeInline(admin.TabularInline):
	model = Equipe
	extra = 0

@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
	list_display = ('simbolo','nome',)

@admin.register(HistAfastamento)
class HistAfastamentoAdmin(admin.ModelAdmin):
	search_fields = ('fk_afastamento__tipificacao','fk_servidor__nome', 'fk_afastamento__id_afastamento')

	list_display = ('fk_servidor','data_inicial','data_final','fk_afastamento')
	autocomplete_fields = ['fk_servidor']

@admin.register(HistFuncao)
class HistFuncaoAdmin(admin.ModelAdmin):
	search_fields = ('fk_servidor__nome','fk_funcao__nome')
	list_display = ('fk_servidor','data_inicio','data_final','fk_funcao')
	autocomplete_fields = ['fk_servidor']

@admin.register(HistLotacao)
class HistLotacaoAdmin(admin.ModelAdmin):
	change_form_template = 'admin/namp/histlotacao/change_form.html'
	search_fields = ('fk_servidor__nome','fk_equipe__nome', 'fk_equipe__fk_setor__nome')
	list_display = ('fk_servidor','data_inicial','data_final', 'fk_equipe', 'fk_setor')	
	list_filter = 'fk_setor',
	date_hierarchy = 'data_inicial'

@admin.register(HistStatusFuncional)
class HistStatusFuncionalAdmin(admin.ModelAdmin):
	search_fields = ('fk_servidor__nome', 'fk_status_funcional__nome' )
	autocomplete_fields = ['fk_servidor', 'fk_status_funcional', ]
	list_display = ('id_hist_funcional','data_inicial', 'data_final', 'fk_servidor', 'fk_status_funcional')
	date_hierarchy = 'data_inicial'

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
	change_form_template = 'admin/namp/jornada/change_form.html'
	search_fields = ['fk_servidor__nome','fk_equipe__fk_setor__nome']
	autocomplete_fields = ['fk_servidor']
	list_filter = ('assiduidade','fk_tipo_jornada')
	date_hierarchy = 'data_jornada'
	list_display = ('get_matricula','get_vinculo','fk_servidor','get_cpf', 'get_codigo_setor','get_nome_setor','get_carga_horaria','get_inicio', 'get_fim')
	list_per_page = 25
	
	admin.site.disable_action('delete_selected')

	def get_matricula(self, obj):
		return obj.fk_servidor.id_matricula
	get_matricula.short_description = 'matrícula' 

	def get_vinculo(self, obj):
		return obj.fk_servidor.vinculo
	get_vinculo.short_description = 'vínculo'
	
	def get_cpf(self, obj):
		return obj.fk_servidor.cpf
	get_cpf.short_description = 'cpf'

	def get_codigo_setor(self, obj):
		return obj.fk_equipe.fk_setor.id_setor
	get_codigo_setor.short_description = 'código'

	def get_nome_setor(self, obj):
		return obj.fk_equipe.fk_setor.nome
	get_nome_setor.short_description = 'setor'

	def get_carga_horaria(self, obj):
		return obj.fk_tipo_jornada.carga_horaria
	get_carga_horaria.short_description = 'carga horária'

	def get_inicio(self, obj):
		inicio = obj.data_jornada.strftime("%d/%m/%Y") + " " +obj.fk_equipe.hora_inicial.strftime("%H:%M:%S")
		return inicio
	get_inicio.short_description = 'início'
	
	def get_fim(self, obj):
		inicio = obj.data_jornada.strftime("%d/%m/%Y") + " " +obj.fk_equipe.hora_inicial.strftime("%H:%M:%S")
		inicioDateTime = DateTime.strptime(inicio, '%d/%m/%Y %H:%M:%S')
		fim = inicioDateTime + TimeDelta(hours=(obj.fk_tipo_jornada.carga_horaria))
		return fim.strftime('%d/%m/%Y %H:%M:%S')
	get_fim.short_description = 'fim'

@admin.register(Regiao)
class RegiaoAdmin(admin.ModelAdmin):
	change_list_template = 'admin/namp/regiao/change_list.html'
	list_display = ('nome', 'get_setor_count')

	def get_setor_count(self, obj):
		return Setor.objects.filter(fk_regiao=obj, status=True).count()
	get_setor_count.short_description = 'Setores'  #Renames column head

	def changelist_view(self, request, extra_context=None):
		#todas as instâncias de Setor do banco de dados
		queryset = Regiao.objects.all()
		regioes = ['Região ' + str(obj.id_regiao) for obj in queryset]
		setores = [int(obj.setor_set.count()) for obj in queryset]

		regioes_json = json.dumps(list(regioes), cls=DjangoJSONEncoder)
		setores_json = json.dumps(list(setores), cls=DjangoJSONEncoder)

		extra_context = extra_context or {"regioes": regioes_json, "setores": setores_json}

		return super().changelist_view(request,extra_context=extra_context)

@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin): 
	form = ServidorFormAdmin	
	change_form_template = 'admin/namp/servidor/change_form.html'
	change_list_template = 'admin/namp/servidor/change_list.html'

	list_per_page = 20
	search_fields = ('nome','fk_equipe__nome', 'fk_equipe__fk_setor__nome')

	radio_fields = {'sexo': admin.HORIZONTAL, 'regime_juridico': admin.HORIZONTAL, 'tipo_vinculo': admin.VERTICAL}
	'''
	Abaixo: apresentação dos forms da model ContatoServ dentro do form da model Servidor
	'''

	list_display = ('nome', 'id_matricula', 'vinculo','cpf','dt_nasc','cargo','cf','tipo_vinculo','regime_juridico','situacao', 'fk_equipe', 'get_setor')
	list_filter = ('cargo','situacao')

	fieldsets = (
		('Dados Pessoais',{
				'fields': (('nome','cpf'), ('sexo','dt_nasc'))
		}),
		('Dados Funcionais',{
				'fields': (('id_matricula','vinculo'), ('tipo_vinculo', 'regime_juridico'), ('cargo','cf', 'situacao'),'fk_setor', 'fk_equipe', 'fk_user')
		}),
		('Contato ',{
				'fields': (('contato'),)
		}),
	)

	inlines = [EnderecoServInline ]

	def change_view(self, request, object_id, form_url='', extra_context=None):
		try:
			return super(ServidorAdmin, self).change_view(request, object_id, form_url, extra_context)
		except ValidationError as e:
			return handle_exception(self, request, e)

	def get_setor(self, obj):
		return Setor.objects.get(id_setor=obj.fk_equipe.fk_setor.id_setor)
	get_setor.short_description = 'Unidade Operacional'  #Renames column head
	get_setor.admin_order_field = 'nome'

	class Media:
		js = ("jquery.mask.min.js",
			  "mascara.js",)

class EnderecoSetorInline(admin.StackedInline):
	model = EnderecoSetor
	fieldsets = (
		(None, {
			'fields': (('uf', 'municipio'), 'cep', ('endereco', 'bairro'), ('numero', 'complemento'))
	            }),
	)

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
	list_per_page = 15
	list_filter = ('fk_regiao','status','setor_sede',)
	list_display = ('id_setor', 'nome','fk_regiao','status', 'setor_sede', 'get_total_servidor')
	search_fields = ('nome','fk_regiao__nome', 'id_setor')
	inlines = [EnderecoSetorInline,EquipeInline]
	#search_fields = ['nome']

	def get_total_servidor(self, obj):
		return Servidor.objects.filter(fk_equipe__in=Equipe.objects.filter(fk_setor=obj)).count() #total servidores do setor
	get_total_servidor.short_description = 'Servidores'  #Nome da coluna
	get_total_servidor.admin_order_field = 'nome'

@admin.register(StatusFuncional)
class StatusFuncionalAdmin(admin.ModelAdmin):
	search_fields = ('nome', )
	list_display = ('codigo_status_funcional','nome')

@admin.register(TipoJornada)
class TipoJornadaAdmin(admin.ModelAdmin):
	list_display = ('carga_horaria', 'tipificacao', 'descricao')

@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
	list_display = ('data_inicial', 'data_final')