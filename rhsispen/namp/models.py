from django.db import models
from django.contrib.auth.models import User
from django import forms
from datetime import timedelta as TimeDelta, datetime as DateTime, date as Date

from django.db.models.fields import AutoField

# Create your models here.
'''CLASSES SEM CHAVE ESTRANGEIRA'''

class Regiao(models.Model):
	id_regiao = models.AutoField(primary_key=True)
	nome = models.CharField(max_length=100, unique=True)
	def __str__(self):
		return self.nome
	class Meta:
		ordering = ["nome"]
		verbose_name = "Região"
		verbose_name_plural = "Regiões"

class Funcao(models.Model):
	id_funcao = models.AutoField(primary_key=True) #Cod com a secad
	simbolo = models.CharField('Símbolo',max_length=25)
	nome = models.CharField(max_length=150,unique=True)
	def __str__(self):
		return self.nome
	class Meta:
		ordering = ['simbolo']
		verbose_name = "Tipo de Função"
		verbose_name_plural = "Tipos de Funções"
		unique_together = ('nome',)

class Afastamento(models.Model):
	id_afastamento = models.AutoField(primary_key=True)
	codigo_afastamento = models.CharField('Código', max_length=10) #Cod com a secad
	tipificacao = models.CharField('Tipo de afastamento', max_length=100, unique=True)
	descricao = models.TextField('Descrição',max_length=100)
	def __str__(self):
		return self.tipificacao
	class Meta:
		ordering = ['id_afastamento']
		verbose_name = "Tipo de Afastamento"
		verbose_name_plural = "Tipos de Afastamento"

class TipoJornada(models.Model):
	id_tipo_jornada = models.AutoField(primary_key=True)
	carga_horaria = models.PositiveIntegerField()
	tipificacao = models.CharField(max_length=100,unique=True)
	descricao = models.TextField(max_length=100)
	def __str__(self):
		return self.tipificacao
	class Meta:
		ordering = ["tipificacao"]
		verbose_name = "Tipo de Jornada"
		verbose_name_plural = "Tipos de Jornadas"

class StatusFuncional(models.Model):
	id_status_funcional = models.AutoField(primary_key=True)
	codigo_status_funcional = models.CharField('Código', max_length=10)
	nome = models.CharField(max_length=50,unique=True)
	descricao = models.TextField(max_length=100)	
	def __str__(self):
		return self.nome	
	
	class Meta:
		ordering = ["nome"]
		verbose_name = "Tipo de Status Funcional"
		verbose_name_plural = "Tipos de Status Funcional"

''' CLASSES COM CHAVE ESTRANGEIRA'''

'''OneToOneField =1..1
   Foreignkey = 1..*
   ManyToManyField = *..*
   SET_DEFAULT = se apagado a referencia, vai pra outra tabela determinada
'''

class Setor(models.Model):
	id_setor = models.CharField('Código', primary_key=True, max_length=50)
	nome = models.CharField(max_length=100, unique=True)
	status = models.BooleanField('Setor Ativo', default=False) #mudar pra o nome da variael = setor_ativo
	setor_sede = models.BooleanField(default=False)
	#RESTRICT: proibe a exclussão de região referenciada em setor
	fk_regiao = models.ForeignKey(Regiao, on_delete = models.RESTRICT, verbose_name='Região')
	def __str__(self):
		return self.nome
	class Meta:
		ordering = ['nome']
		verbose_name = "Setor"
		verbose_name_plural = "Setores"
		#Campos que devem ser únicos juntos
		unique_together = ('id_setor','nome', 'fk_regiao')

class EnderecoSetor(models.Model):
	id_endereco_setor = models.AutoField(primary_key=True)
	uf = models.CharField(max_length=2, default='TO')
	cep = models.CharField(max_length=8, blank=True, default='77000000')
	municipio = models.CharField(max_length=100, default='Não registrado')
	endereco = models.CharField(max_length=100, default='Não registrado')
	numero = models.CharField(max_length=10, blank=True)
	bairro = models.CharField(max_length=100, blank=True)
	complemento = models.CharField(max_length=100, blank=True)
	#CASCATE: se excluido o setor, será excluido o objeto referenciado(endereco_setor)
	fk_setor = models.OneToOneField(Setor, on_delete = models.RESTRICT, verbose_name='Setor')
	def __str__(self):
		return ' - '
	class Meta:
		ordering = ["uf","municipio", "endereco"]
		verbose_name = "Endereço do Setor"
		verbose_name_plural = "Enderecos dos Setores"

class Equipe(models.Model):
	id_equipe = models.AutoField(primary_key=True)
	nome = models.CharField(max_length=50)
	status = models.BooleanField('Equipe Ativa',default=False)
	hora_inicial = models.TimeField(auto_now= False, auto_now_add=False)
	CHOICES_CATEGORIA = [('Plantão','Plantão'),('Expediente','Expediente')]
	categoria = models.CharField('Categoria', max_length=10, choices=CHOICES_CATEGORIA)
	fk_setor = models.ForeignKey(Setor, on_delete = models.RESTRICT, verbose_name='Setor')
	fk_tipo_jornada = models.ForeignKey(TipoJornada, on_delete = models.RESTRICT, verbose_name='Tipo de Jornada')
	
	deleted_on = models.DateTimeField(null=True, blank=True, verbose_name='Data da exclusão')

	def delete(self):
		self.deleted_on = DateTime.now()
		self.status = False
		self.save()

	def __str__(self):
		return self.nome
	
	def get_servidores(self):
		return Servidor.objects.filter(fk_equipe=self.id_equipe).count()

	class Meta:
		ordering = ["nome"]
		verbose_name = "Equipe"
		verbose_name_plural = "Equipes"
		#Campos que devem ser únicos juntos
		unique_together = ('nome', 'fk_setor',)

class ContatoEquipe(models.Model):
	CELULAR = 'Telefone Celular'
	FIXO = 'Telefone Fixo'
	EMAIL = 'E-mail'

	CONTATOS_CHOICES = (
	    (CELULAR,'Telefone Celular'), 
	    (FIXO,'Telefone Fixo'),
	    (EMAIL,'E-mail'),
	)
	id_contato_equipe = models.AutoField(primary_key=True)
	tipificacao = models.CharField('Tipo de contato', max_length=50, choices=CONTATOS_CHOICES)
	contato = models.CharField(max_length=50)
	fk_equipe = models.ForeignKey(Equipe, on_delete = models.RESTRICT, verbose_name='Equipe')
	def __str__(self):
		return self.contato + ' ' + str(self.fk_equipe)
	class Meta:
		verbose_name = "Contato da Equipe"
		verbose_name_plural = "Contatos da Equipe"

class Servidor(models.Model):
	id_matricula = models.CharField('Matrícula', primary_key=True, max_length=30)
	vinculo = models.CharField('Vínculo',max_length=2) #Parte da matricula
	nome = models.CharField(max_length=100)
	cpf = models.CharField('CPF',max_length=11, unique=True)
	CHOICES_SEXO = [('M','Masculino'),('F','Feminino')]
	sexo = models.CharField('Sexo', max_length=1, choices=CHOICES_SEXO)
	dt_nasc = models.DateField('Data de Nascimento')
	CHOICES_CARGO = [
		('Agente de Execução Penal','Agente de Execução Penal'),
		('Agente Analista em Execução Penal','Agente Analista em Execução Penal'),
		('Assistente Administrativo','Assistente Administrativo'),
		('Auxiliar Administrativo','Auxiliar Administrativo'),
		('Auxiliar de Serviços Gerais','Auxiliar de Serviços Gerais'),
		('Agente Socioeducativo','Agente Socioeducativo'),
		('Agente de Segurança Socioeducativo','Agente de Segurança Socioeducativo'),
		('Agente Especialista Socioeducativo','Agente Especialista Socioeducativo'),
	]
	cargo = models.CharField(max_length=50, choices=CHOICES_CARGO)
	CHOICES_CF = [
		('I', 'I'),
		('II', 'II'),
		('Nenhum', 'Nenhum'),
	]
	cf = models.CharField('Curso de Formação',max_length=10, choices=CHOICES_CF)
	tipo_vinculo = models.CharField('Tipo de Vínculo',max_length=50)
	CHOICES_VINCULO = [
		('Contrato', 'Contrato'),
		('Concursado', 'Concursado'),
		('Estágio', 'Estágio'),
		('Jovem Aprendiz', 'Jovem Aprendiz'),
		('Terceirizado', 'Terceirizado'),
	]
	tipo_vinculo = models.CharField('Tipo de Vínculo',max_length=25, choices=CHOICES_VINCULO)
	CHOICES_JURIDICO = [('CLT','CLT'),('Estatutário','Estatutário')]
	regime_juridico = models.CharField('Regime Jurídico',max_length=25, choices=CHOICES_JURIDICO)
	situacao = models.BooleanField('Servidor Ativo', default=False)
	contato = models.CharField('Número para contato: ', max_length=11, blank=True, null=True)
	fk_setor = models.ForeignKey(Setor, on_delete = models.RESTRICT, verbose_name='Setor')
	fk_equipe = models.ForeignKey(Equipe, on_delete = models.RESTRICT, verbose_name='Equipe')
	fk_user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.nome

	class Meta:
		ordering = ['nome']
		verbose_name = "Servidor"
		verbose_name_plural = "Servidores"
		#Campos que devem ser únicos juntos
		unique_together = ('id_matricula','vinculo','cpf',)

class EnderecoServ(models.Model):
	id_endereco_serv = models.AutoField(primary_key=True)
	uf = models.CharField(max_length=2) 
	cep = models.CharField(max_length=8)
	municipio = models.CharField(max_length=100)
	endereco = models.CharField(max_length=100)
	numero = models.CharField(max_length=10)
	bairro = models.CharField(max_length=100)
	complemento = models.CharField(max_length=100, blank=True)
	fk_servidor = models.OneToOneField(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	def __str__(self):
		return '-'
	class Meta:
		ordering = ["uf","municipio", "endereco"]
		verbose_name = "Endereço do Servidor"
		verbose_name_plural = "Endereço do Servidor"

class HistFuncao(models.Model):
	id_hist_funcao = models.AutoField(primary_key=True)
	data_inicio = models.DateField()
	data_final = models.DateField(blank=True, null=True)
	fk_funcao = models.ForeignKey(Funcao, on_delete = models.RESTRICT, verbose_name='Função')
	fk_servidor = models.ForeignKey(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	def __str__(self):
		return str(self.fk_servidor)
	class Meta:
		verbose_name = "Função"
		verbose_name_plural = "Funções"


class HistAfastamento(models.Model):
	id_hist_afastamento = models.AutoField(primary_key=True)
	data_inicial = models.DateField()
	data_final = models.DateField()
	fk_afastamento = models.ForeignKey(Afastamento, on_delete = models.RESTRICT, verbose_name='Afastamento')
	fk_servidor = models.ForeignKey(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	def __str__(self):
		return str(self.id_hist_afastamento)
	class Meta:
		verbose_name = "Afastamento"
		verbose_name_plural = "Afastamentos"

class HistLotacao(models.Model):
	id_hist_lotacao = models.AutoField(primary_key=True)
	data_inicial =	models.DateField()
	data_final = models.DateField(blank=True, null=True)
	fk_servidor = models.ForeignKey(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	fk_setor = models.ForeignKey(Setor, on_delete = models.RESTRICT, verbose_name='Setor')
	fk_equipe = models.ForeignKey(Equipe, on_delete = models.RESTRICT, verbose_name='Equipe')
	def __str__(self):
		return str(self.id_hist_lotacao)
	class Meta:
		verbose_name = "Lotação"
		verbose_name_plural = "Lotações"


class HistStatusFuncional(models.Model):
	id_hist_funcional = models.AutoField(primary_key=True)
	data_inicial = models.DateField()
	data_final = models.DateField()
	fk_servidor = models.ForeignKey(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	fk_status_funcional = models.ForeignKey(StatusFuncional, on_delete = models.RESTRICT, verbose_name='Status Funcional')
	def __str__(self):
		return str(self.id_hist_funcional)
	class Meta:
		verbose_name = "Status Funcional"
		verbose_name_plural = "Status Funcional"

class Jornada(models.Model):
	id_jornada = models.AutoField(primary_key=True)
	data_jornada = models.DateField()
	assiduidade = models.BooleanField(default=False)
	fk_afastamento = models.ForeignKey(Afastamento, on_delete = models.RESTRICT,verbose_name='Motivo da Ausência',blank=True, null=True)
	fk_servidor = models.ForeignKey(Servidor, on_delete = models.RESTRICT, verbose_name='Servidor')
	fk_equipe = models.ForeignKey(Equipe, on_delete = models.RESTRICT, verbose_name='Equipe')
	fk_tipo_jornada = models.ForeignKey(TipoJornada, on_delete = models.RESTRICT, verbose_name='Tipo Jornada')
	
	def __str__(self):
		return str(self.id_jornada) 
	
	class Meta:
		ordering = ["fk_equipe__fk_setor__nome","fk_equipe__nome","fk_servidor__nome", "data_jornada"]
		verbose_name = "Jornada"
		verbose_name_plural = "Jornadas"
		unique_together = ('fk_servidor','data_jornada',)

class Periodo(models.Model):
	id_periodo_acao = models.AutoField(primary_key=True)
	data_inicial = models.DateField()
	data_final = models.DateField()
	descricao = models.CharField(max_length=25)

class Acao