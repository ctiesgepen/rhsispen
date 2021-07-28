#from models import HistFuncao
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from namp.models import Servidor, HistFuncao, HistLotacao, HistAfastamento, Jornada, Equipe
import datetime

'''
	Este Signal popula a tabela HistLotação sempre que uma
	instância de Servidor for criada ou modificada. No entanto,
	havendo modificação de uma instância de Servidor, o HistLoação
	anterior é atualizado com a data atual e o novo HistLotação é
	criado.
'''
@receiver(post_save, sender=Servidor)
def post_save_create_histlotacao(sender, instance, created, **kargs):
	if created:
		HistLotacao.objects.create(
			data_inicial=datetime.date.today(),
			fk_servidor=instance,
			fk_setor=instance.fk_setor,
			fk_equipe=instance.fk_equipe)
	else:
		print('Servidor foi alterado.')	
		try:
			print('Buscando lotação do servidor.')	
			oldHistLotacao = HistLotacao.objects.filter(
				fk_servidor=instance,
				data_final__isnull=True).order_by('-data_inicial').first()
		except HistLotacao.DoesNotExist:
			print('Lotação do servidor não foi encontrada e uma nova foi criada.')
			pass
		else:
			print('Lotação do servidor foi encontrada e alterada.')	
			if oldHistLotacao:
				if oldHistLotacao.fk_setor != instance.fk_setor or oldHistLotacao.fk_equipe != instance.fk_equipe:
					oldHistLotacao.data_final = datetime.date.today()
					oldHistLotacao.save()
					HistLotacao.objects.create(
						data_inicial=datetime.date.today(),
						fk_servidor=instance,
						fk_setor=instance.fk_setor,
						fk_equipe=instance.fk_equipe)
					jornadas = Jornada.objects.filter(fk_servidor=instance,data_jornada__gte=datetime.date.today())
					if jornadas:
						for jornada in jornadas: 
							jornada.delete()
			else:
				HistLotacao.objects.create(
					data_inicial=datetime.date.today(),
					fk_servidor=instance,
					fk_setor=instance.fk_setor,
					fk_equipe=instance.fk_equipe)

				jornadas = Jornada.objects.filter(fk_servidor=instance,data_jornada__gte=datetime.date.today())
				if jornadas:
					for jornada in jornadas: 
						jornada.delete()


'''
'''
@receiver(pre_save, sender=HistAfastamento)
def pre_save_update_jornada(sender, instance, **kargs):
	if HistAfastamento.objects.filter(id_hist_afastamento=instance.id_hist_afastamento).count() != 0:
		oldHistAfastamento = HistAfastamento.objects.get(id_hist_afastamento=instance.id_hist_afastamento)
		print(oldHistAfastamento.id_hist_afastamento, oldHistAfastamento.fk_afastamento)
		print(instance.id_hist_afastamento, instance.fk_afastamento)
		if((oldHistAfastamento.fk_afastamento != instance.fk_afastamento) or
			(oldHistAfastamento.fk_servidor != instance.fk_servidor) or
			(oldHistAfastamento.data_inicial != instance.data_inicial) or
			(oldHistAfastamento.data_final != instance.data_final)):
			
			jornadas = Jornada.objects.filter(
				fk_servidor=oldHistAfastamento.fk_servidor,
				data_jornada__range=[oldHistAfastamento.data_inicial, oldHistAfastamento.data_final])
			if jornadas:
				for jornada in jornadas:
					jornada.assiduidade = True
					jornada.fk_afastamento = None
					jornada.save()
					print('jornadas restaudatas!')

			jornadas = Jornada.objects.filter(
				fk_servidor=instance.fk_servidor).filter(
				data_jornada__range=[instance.data_inicial, instance.data_final])
			if jornadas:
				for jornada in jornadas:
					jornada.assiduidade = False
					jornada.fk_afastamento = instance.fk_afastamento
					jornada.save()
					print('jornadas atualizadas!')					

'''
	Este Signal desmarca a assiduidade e lança o tipo de afastamento
	nas jornadas existentes dentro do período do afastamento que 
	esteja sendo criado para o servidor vinculado a ele.
'''
@receiver(post_save, sender=HistAfastamento)
def post_save_create_afastamento(sender, instance, created, **kargs):
	if created:
		try:
			jornadas = Jornada.objects.filter(
				fk_servidor=instance.fk_servidor).filter(
				data_jornada__range=[instance.data_inicial, instance.data_final])
		except Jornada.DoesNotExist:
			pass
		else:
			if jornadas:
				for jornada in jornadas:
					jornada.assiduidade = False
					jornada.fk_afastamento = instance.fk_afastamento
					jornada.save()
					print('Entrei aqui também! Novo Afastamento')

@receiver(post_save, sender=HistAfastamento)
def post_save_create_afastamento(sender, instance, created, **kargs):
	if created:
		try:
			jornadas = Jornada.objects.filter(
				fk_servidor=instance.fk_servidor).filter(
				data_jornada__range=[instance.data_inicial, instance.data_final])
		except Jornada.DoesNotExist:
			pass
		else:
			if jornadas:
				for jornada in jornadas:
					jornada.assiduidade = False
					jornada.fk_afastamento = instance.fk_afastamento
					jornada.save()
					print('Entrei aqui também! Novo Afastamento')
		
'''
	Este Signal desmarca a assiduidade e lança o tipo de afastamento
	numa jornada que esteja sendo criada dentro do período de um 
	afastamento já existente para o servidor vinculado a ela.
'''
@receiver(post_save, sender=Jornada)
def post_save_create_jornada(sender, instance, created, **kargs):
	if created:
		if HistAfastamento.objects.filter(fk_servidor=instance.fk_servidor).count() != 0:
			myHistAfastamento = HistAfastamento.objects.filter(fk_servidor=instance.fk_servidor)
			for afastamento in myHistAfastamento:
				for	data in range(afastamento.data_inicial.toordinal(), afastamento.data_final.toordinal()+1):
					if instance.data_jornada.toordinal() == data:
						instance.assiduidade = False
						instance.fk_afastamento = afastamento.fk_afastamento
						instance.save()	
						print('entrei aqui também! Nova Jornada')


'''
Att dos Historicos de funçoes
'''
@receiver(post_save, sender=HistFuncao)
def post_save_create_histfuncao(sender, instance,created, **kargs):
	if created:
		try:
			oldHistFuncao = HistFuncao.objects.filter(
				fk_servidor=instance.fk_servidor,
				data_final__isnull=True).exclude(data_inicio__in=[datetime.date.today()],
				fk_funcao=instance.fk_funcao).order_by('-data_inicio').last()
		except HistFuncao.DoesNotExist:
			print('Historico de funcao nao encontrado.')
			pass
		else:
			if oldHistFuncao:
				oldHistFuncao.data_final = datetime.date.today()
				oldHistFuncao.save()

'''
	Att dos Equipe: o admin restaura o status ativo para uma equipe anteriormente
	deletada pelo operador. A equipe volta a ser exibida para o operador
'''
@receiver(post_save, sender=Equipe)
def post_save_equipe(sender, instance,created, **kargs):
	if not created:
		if instance.status and instance.deleted_on is not None:
			instance.deleted_on = None
			instance.save()
