from django import forms
from .models import TipoJornada, Setor, Equipe, Servidor
from functools import partial
from django.forms import ModelForm

DateInput = partial(forms.DateInput, {'class': 'datepicker'})
    
class DefinirJornadaRegularForm(forms.Form):   
    setor = forms.CharField(required=False, label='Código da Unidade')
    data_inicial = forms.DateField(widget=DateInput(),required=True)    
    data_final = forms.DateField(widget=DateInput(),required=True)  
    # o tipo de jornada define a escala sob qual deve ser gerada a joranada
    equipe = forms.ChoiceField(choices = [('', '--Selecione--')] )
    #tipo_jornada = forms.ChoiceField(choices = [('', '--Selecione--')] )

    def __init__(self, *args, **kwargs):
        super(DefinirJornadaRegularForm, self).__init__(*args, **kwargs)
        self.fields['setor'].widget.attrs['readonly'] = True
        self.fields['data_inicial'].widget.attrs['readonly'] = True
        self.fields['data_final'].widget.attrs['readonly'] = True
        self.fields['equipe'].choices = [('', '--Selecione--')] + list(Equipe.objects.all().values_list('id_equipe', 'nome'))
        #self.fields['tipo_jornada'].choices = [('', '--Selecione--')] + list(TipoJornada.objects.all().values_list('carga_horaria', 'tipificacao'))

class GerarJornadaRegularForm(forms.Form):
    equipe_plantao12h = forms.ChoiceField(required=True,choices = [('', '--Selecione--')],label='1º PLANTÃO de 12H do mês:')
    data_plantao12h = forms.DateField(required=True,widget=DateInput(),label='Data de entrada:')
    equipe_plantao24h = forms.ChoiceField(required=True,choices = [('', '--Selecione--')],label='1º PLANTÃO de 24H do mês:')
    data_plantao24h = forms.DateField(required=True,widget=DateInput(),label='Data de entrada:')
    equipe_plantao48h = forms.ChoiceField(required=True,choices = [('', '--Selecione--')],label='1º PLANTÃO de 48H do mês:')
    data_plantao48h = forms.DateField(required=True,widget=DateInput(),label='Data de entrada:')
    
    def __init__(self, *args, **kwargs):
        super(GerarJornadaRegularForm, self).__init__(*args, **kwargs)
        self.fields['equipe_plantao12h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=12).values_list('id_equipe', 'nome'))
        self.fields['equipe_plantao24h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=24).values_list('id_equipe', 'nome'))
        self.fields['equipe_plantao48h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=48).values_list('id_equipe', 'nome'))
        self.fields['data_plantao12h'].widget.attrs['readonly'] = True
        self.fields['data_plantao24h'].widget.attrs['readonly'] = True
        self.fields['data_plantao48h'].widget.attrs['readonly'] = True
        self.fields['equipe_plantao12h'].required = args[len(args)-1]['tem_plantao12']
        self.fields['data_plantao12h'].required = args[len(args)-1]['tem_plantao12']
        self.fields['equipe_plantao24h'].required = args[len(args)-1]['tem_plantao24']
        self.fields['data_plantao24h'].required = args[len(args)-1]['tem_plantao24']
        self.fields['equipe_plantao48h'].required = args[len(args)-1]['tem_plantao48']
        self.fields['data_plantao48h'].required = args[len(args)-1]['tem_plantao48']

class ServidorFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServidorFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cpf'].widget.attrs={"placeholder":"000.000.000-00"} #Aparece no campo digitavel do usuario
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['dt_nasc'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['dt_nasc'].widget.attrs['class'] = 'mask-dt'
 
class EnderecoFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EnderecoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cep'].widget.attrs={"placeholder":"00000-000"}       
        self.fields['cep'].widget.attrs['class'] = 'mask-cep'

class TextFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TextFormAdmin, self).__init__(*args, **kwargs)
        self.fields['descricao'].widget.attrs={"placeholder":
                                               "Digite com detalhamento",
                                               "rows": 15,
                                               "cols": 50}

class HoraFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HoraFormAdmin, self).__init__(*args, **kwargs)
        self.fields['hora_inicial'].widget.attrs={"placeholder":"00:00"} 
        self.fields['hora_inicial'].widget.attrs['class'] = 'mask-hr'

class HistStatusFuncionalFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HistStatusFuncionalFormAdmin, self).__init__(*args, **kwargs)
        self.fields['data_inicial'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['data_inicial'].widget.attrs['class'] = 'mask-dt'
        self.fields['data_final'].widget.attrs = {"placeholder":"00/00/0000"}
        self.fields['data_final'].widget.attrs['class'] = 'mask-dt'

class HistAfastamentoFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HistAfastamentoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['data_inicial'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['data_inicial'].widget.attrs['class'] = 'mask-dt'
        self.fields['data_final'].widget.attrs = {"placeholder":"00/00/0000"}
        self.fields['data_final'].widget.attrs['class'] = 'mask-dt'

class HistFuncaoFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HistFuncaoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['data_inicio'].widget.attrs['class'] = 'mask-dt'
        self.fields['data_final'].widget.attrs = {"placeholder":"00/00/0000"}
        self.fields['data_final'].widget.attrs['class'] = 'mask-dt'

#class HistFuncaoFomAdmin(forms.ModelForm):
class HistLotacaoFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HistLotacaoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['data_inicial'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['data_inicial'].widget.attrs['class'] = 'mask-dt'
        self.fields['data_final'].widget.attrs = {"placeholder":"00/00/0000"}
        self.fields['data_final'].widget.attrs['class'] = 'mask-dt'

class JornadaFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JornadaFormAdmin, self).__init__(*args, **kwargs)
        self.fields['data_jornada'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['data_jornada'].widget.attrs['class'] = 'mask-dt'

class TimeInput(forms.TimeInput):
    input_type = "time"

'''
Formulário de adição de equipes. Cria-se o formulário a partir
do modelo que se quer trabalhar. Neste caso, o model Equipe.
'''
class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hora_inicial'].widget = TimeInput()
        

class EquipeSearchForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ('nome', )
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite um nome de equipe'}),
        }

class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fk_equipe'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_setor=self.instance.fk_setor).values_list('id_equipe', 'nome'))
        for field in self.fields:
            if field =='fk_equipe': continue
            self.fields[field].widget.attrs['readonly'] = True
            #Falta setar o choices    
class ServidorSearchForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ('nome', )
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite um nome de servidor'}),
        }
  #  def __init__(self, *args, **kwargs):
  #    super().__init__(*args, **kwargs)
  #      self.fields['nome', ].widget.attrs={"placeholder":"Digite o nome do servidor"}
