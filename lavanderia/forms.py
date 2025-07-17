from django import forms
from .models import *
from django.core.exceptions import ValidationError

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = '__all__'
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'tamanho': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade < 0:
            raise ValidationError("A quantidade não pode ser negativa.")
        return quantidade

class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = '__all__'
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 999}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'servico': forms.Select(attrs={'class': 'form-control', }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tamanho': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'retornou': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantidade_solicitada = cleaned_data.get('quantidade')
        categoria = cleaned_data.get('categoria')
        tamanho = cleaned_data.get('tamanho')
        
        # Obter a quantidade anterior se for uma atualização
        quantidade_anterior = 0
        if self.instance.pk:
            quantidade_anterior = OrdemServico.objects.get(pk=self.instance.pk).quantidade
        
        diferenca_para_retirar = quantidade_solicitada - quantidade_anterior

        if categoria and tamanho:
            try:
                inventario_item = Inventario.objects.get(categoria=categoria, tamanho=tamanho)
                
                # Validação de estoque apenas se a quantidade solicitada for maior que a anterior
                if diferenca_para_retirar > 0 and inventario_item.quantidade < diferenca_para_retirar:
                    self.add_error(
                        'quantidade',
                        f'Estoque insuficiente em Inventário. Disponível: {inventario_item.quantidade}. '
                        f'Necessário: {diferenca_para_retirar} para esta operação.'
                    )
            except Inventario.DoesNotExist:
                self.add_error(
                    None, # Erro não ligado a um campo específico
                    f'Não há registro de inventário para a categoria "{categoria.nome}" e tamanho "{tamanho}".'
                )
        
        # Validação para 'retornou'
        retornou_quantidade = cleaned_data.get('retornou', 0)
        if retornou_quantidade > quantidade_solicitada:
            self.add_error('retornou', 'A quantidade retornada não pode ser maior que a quantidade total da ordem de serviço.')

        return cleaned_data