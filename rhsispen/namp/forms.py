from django import forms
from .models import * 
from functools import partial
from django.forms import ModelForm
from django.forms import DateTimeInput, DateInput

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

DateTimeInput = partial(forms.DateTimeInput, {'class':'datepicker'})

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
    data_plantao12h = forms.DateField(required=True,label='Data de entrada:')
    equipe_plantao24h = forms.ChoiceField(required=True,choices = [('', '--Selecione--')],label='1º PLANTÃO de 24H do mês:')
    data_plantao24h = forms.DateField(required=True,label='Data de entrada:')
    equipe_plantao48h = forms.ChoiceField(required=True,choices = [('', '--Selecione--')],label='1º PLANTÃO de 48H do mês:')
    data_plantao48h = forms.DateField(required=True,label='Data de entrada:')
    
    def __init__(self, *args, **kwargs):
        super(GerarJornadaRegularForm, self).__init__(*args, **kwargs)
        self.fields['equipe_plantao12h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=12).values_list('id_equipe', 'nome'))
        self.fields['equipe_plantao24h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=24).values_list('id_equipe', 'nome'))
        self.fields['equipe_plantao48h'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_tipo_jornada__carga_horaria=48).values_list('id_equipe', 'nome'))
        self.fields['data_plantao12h'].widget = DateInput()
        self.fields['data_plantao24h'].widget = DateInput()
        self.fields['data_plantao48h'].widget = DateInput()
        '''                     self.fields['equipe_plantao12h'].required = args[len(args)-1]['tem_plantao12']
                                self.fields['data_plantao12h'].required = args[len(args)-1]['tem_plantao12']
                                self.fields['equipe_plantao24h'].required = args[len(args)-1]['tem_plantao24']
                                self.fields['data_plantao24h'].required = args[len(args)-1]['tem_plantao24']
                                self.fields['equipe_plantao48h'].required = args[len(args)-1]['tem_plantao48']
                                self.fields['data_plantao48h'].required = args[len(args)-1]['tem_plantao48']'''

class ServidorFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServidorFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cpf'].widget.attrs={"placeholder":"000.000.000-00"} #Aparece no campo digitavel do usuario
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['dt_nasc'].widget.attrs={"placeholder":"00/00/0000"}
        self.fields['dt_nasc'].widget.attrs['class'] = 'mask-dt'
       # if self.objects.filter(Servidor.tipo_contato == 'Celular')
        self.fields['contato'].widget.attrs={"placeholder":"(00) 90000-0000"}
        self.fields['contato'].widget.attrs['class'] = 'mask-contato'
        #    else:
         #   self.fields['contato'].widget.attrs={"placeholder": "(00) 0000-0000"}
          #  self.fields['contato'].widget.attrs['class'] = 'mask-contato'


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

class DateInput(forms.DateInput):
    input_type = 'date'

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)

'''
Formulário de adição de equipes. Cria-se o formulário a partir
do modelo que se quer trabalhar. Neste caso, o model Equipe.
'''
class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        exclude = ('deleted_on',)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = ""

class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fk_equipe'].choices = [('', '--Selecione--')] + list(Equipe.objects.filter(fk_setor=self.instance.fk_setor).values_list('id_equipe', 'nome'))
        
class EnderecosServForm():
    class Meta:
        model = EnderecoServ
        fields = '__all__'

class ServidorSearchForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ('nome',)
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite um nome de servidor'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = ""

class AfastamentoForm(forms.ModelForm):
    class Meta:
        model = HistAfastamento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AfastamentoForm, self).__init__(*args, **kwargs)
        self.fields['data_inicial'].widget = DateInput()
        self.fields['data_final'].widget = DateInput()
        #self.fields['fk_servidor'].choices = [('', '--Selecione--')] + args[len(args)-1]['servidores']

class AfastamentoSearchForm(forms.Form):
    servidor = forms.CharField(required=True)
    class Meta:
        fields = ('servidor', )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servidor'].label = ""
        self.fields['servidor'].widget.attrs['placeholder'] = 'Digite um nome de servidor'

class EscalaFrequenciaForm(forms.ModelForm):
    class Meta:
        model = EscalaFrequencia
        fields = ('data',)
        widgets = {
            'data': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].required = False

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = '__all__'

class EnderecoSetorForm(forms.ModelForm):
    class Meta:
        model = EnderecoSetor
        fields = '__all__'
    
class ServidorMoverForm(forms.Form):
    servidor = forms.ChoiceField(required=True, label='Servidor')
    equipe_origem = forms.ChoiceField(required=True,label='Equipe Atual')
    equipe_destino = forms.ChoiceField(required=True, label='Equipe Destino')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servidor'].choices = [('', '--Selecione--')] + list(Servidor.objects.all().values_list('id_matricula', 'nome'))
        self.fields['equipe_origem'].choices = [('', '--Selecione--')] + list(Equipe.objects.all().values_list('id_equipe', 'nome'))
        self.fields['equipe_destino'].choices = [('', '--Selecione--')] + list(Equipe.objects.all().values_list('id_equipe', 'nome'))

class PeriodoAcaoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcao
        fields = '__all__'
        widgets = {
            'data_inicial': DateTimeInput(),
            'data_final': DateTimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PeriodoAcaoSearchForm(forms.Form):
    descricao = forms.CharField(max_length=25)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descricao'].label = ""
        self.fields['descricao'].widget.attrs['placeholder'] = 'Digite mês ou evento. (Ex. abril, escala)'