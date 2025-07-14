from django.db import models

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


class Item(models.Model):
    STATUS_CHOICES = [
        ('Sujo', 'Sujo'),
        ('Manchado', 'Manchado'),
        ('Lavando', 'Lavando'),
        ('Limpo', 'Limpo'),
        ('Retornou com mancha', 'Retornou com mancha'),
    ]

    TAMANHO_CHOICES = [
        ('PP', 'PP'),
        ('P', 'P'),
        ('M', 'M'),
        ('G', 'G'),
        ('GG', 'GG'),
        ('Único', 'Único'),
        ('Diversos', 'Diversos'),
    ]
    quantidade = models.IntegerField(choices=[(i, str(i)) for i in range(1, 1000)])
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    tamanho = models.CharField(max_length=10, choices=TAMANHO_CHOICES, default='Único')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.categoria.nome} ({self.servico.nome}) - {self.status}'

