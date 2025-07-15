# seu_app/admin.py

from django.contrib import admin
from django.utils.html import format_html
# Certifique-se de importar Inventario aqui
from .models import Servico, Categoria, OrdemServico, Inventario


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Inventario) # Adicionado o registro do Inventario
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['categoria', 'quantidade', 'tamanho', 'observacoes', 'criado_em', 'atualizado_em']
    list_filter = ['categoria', 'tamanho']
    search_fields = ['categoria__nome', 'observacoes']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-criado_em']
    list_per_page = 25

    fieldsets = (
        ('Informações do Inventário', {
            'fields': ('categoria', 'quantidade', 'tamanho', 'observacoes')
        }),
        ('Controle de Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ['quantidade', 'retornou', 'categoria', 'servico', 'tamanho', 'status_colorido', 'criado_em']
    list_filter = ['categoria', 'servico', 'status', 'tamanho']
    search_fields = ['quantidade', 'observacoes', 'categoria__nome', 'servico__nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-criado_em']
    list_per_page = 25

    fieldsets = (
        ('Informações do Item', {
            'fields': ('quantidade', 'retornou', 'categoria', 'servico', 'status', 'tamanho')
        }),
        ('Detalhes Adicionais', {
            'fields': ('observacoes',)
        }),
        ('Controle de Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    def status_colorido(self, obj):
        cores = {
            'Sujo': 'Sienna',
            'Manchado': 'Orange',
            'Lavando': 'DarkOrange',
            'Limpo': 'ForestGreen',
            'Retornou com mancha': 'MediumPurple',
        }
        cor = cores.get(obj.status, 'gray')
        return format_html(f'<span style="color: {cor}; font-weight: bold;">{obj.status}</span>')

    status_colorido.short_description = 'Status'