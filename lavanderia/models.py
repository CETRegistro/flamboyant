# seu_app/models.py

from django.db import models
from django.core.exceptions import ValidationError # Importe ValidationError

class Servico(models.Model):
    """Tipo de serviço: Lavagem simples, à seco, etc"""
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    """Categoria do item: Lençol, Toalha, etc"""
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Inventario(models.Model):
    TAMANHO_CHOICES = [
        ('PP', 'PP'),
        ('P', 'P'),
        ('M', 'M'),
        ('G', 'G'),
        ('GG', 'GG'),
        ('Único', 'Único'),
        ('Diversos', 'Diversos'),
    ]
    # Quantidade real em estoque do inventário
    quantidade = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)    
    tamanho = models.CharField(max_length=10, choices=TAMANHO_CHOICES, default='Único')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que não haja duas entradas de inventário iguais para a mesma categoria e tamanho
        unique_together = ('categoria', 'tamanho')

    def __str__(self):
        return f'{self.categoria.nome} ({self.tamanho}) - Estoque: {self.quantidade}'


class OrdemServico(models.Model): # Modelo da gestão de lavanderia
    STATUS_CHOICES = [
        ('Sujo', 'Sujo'),
        ('Manchado', 'Manchado'),
        ('Lavando', 'Lavando'),
        ('Limpo', 'Limpo'),
        ('Retornou com mancha', 'Retornou com mancha'),
        ('Operação concluída','Operação concluída')
    ]

    TAMANHO_CHOICES = [ # Mantenha choices aqui para o Item
        ('PP', 'PP'),
        ('P', 'P'),
        ('M', 'M'),
        ('G', 'G'),
        ('GG', 'GG'),
        ('Único', 'Único'),
        ('Diversos', 'Diversos'),
    ]
    
    # Campo quantidade, com choices de 1 a 999
    quantidade = models.IntegerField(choices=[(i, str(i)) for i in range(1, 1000)])
    # Relacionamento ForeignKey para Categoria
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    # Campo tamanho, com choices
    tamanho = models.CharField(max_length=10, choices=TAMANHO_CHOICES, default='Único')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    retornou = models.IntegerField(default=0) # Quantidade que retornou ao cliente

    def clean(self):
        # Validação personalizada para verificar o estoque no Inventario
        if self.pk: # Se o item já existe, pegue a quantidade anterior para cálculo
            original_item = OrdemServico.objects.get(pk=self.pk) # Corrigido: OrdemServico
            quantidade_anterior = original_item.quantidade
        else: # Se é um novo item
            quantidade_anterior = 0
        
        # A diferença que está sendo 'retirada' do estoque (se a quantidade aumentou)
        diferenca_para_retirar = self.quantidade - quantidade_anterior

        # Encontra o item de inventário correspondente para a categoria e tamanho
        inventario_item = Inventario.objects.filter(
            categoria=self.categoria,
            tamanho=self.tamanho
        ).first()

        if not inventario_item:
            raise ValidationError(
                f'Não há registro de inventário para a categoria "{self.categoria.nome}" e tamanho "{self.tamanho}".'
            )
        
        # Verifica se há estoque suficiente apenas se a quantidade de Item for aumentar
        if diferenca_para_retirar > 0 and inventario_item.quantidade < diferenca_para_retirar:
            raise ValidationError(
                f'Estoque insuficiente em Inventário para adicionar. Disponível: {inventario_item.quantidade}, '
                f'Necessário: {diferenca_para_retirar} para este item.'
            )
        
        # Validação para 'retornou'
        if self.retornou > self.quantidade:
            raise ValidationError(
                'A quantidade retornada não pode ser maior que a quantidade total da ordem de serviço.'
            )


    def save(self, *args, **kwargs):
        self.full_clean() # Executa as validações definidas em clean()

        # Calcula a diferença para ajustar o inventário
        if self.pk: # Item existente
            original_item = OrdemServico.objects.get(pk=self.pk) # Corrigido: OrdemServico
            quantidade_anterior = original_item.quantidade
            diferenca_para_ajustar = self.quantidade - quantidade_anterior
        else: # Novo item
            diferenca_para_ajustar = self.quantidade

        # Encontra o item de inventário correspondente (já validado em clean())
        inventario_item = Inventario.objects.get(categoria=self.categoria, tamanho=self.tamanho)
        
        # Ajusta a quantidade no inventário
        # Assumindo que a criação/modificação de um Item representa uma "saída" do inventário
        inventario_item.quantidade -= diferenca_para_ajustar
        inventario_item.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.categoria.nome} ({self.servico.nome}) - {self.status}'