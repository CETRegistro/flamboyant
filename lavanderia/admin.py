from django.contrib import admin
from django.utils.html import format_html
from .models import Servico, Categoria, Item


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['quantidade', 'categoria', 'servico', 'tamanho', 'status_colorido', 'criado_em']
    list_filter = ['categoria', 'servico', 'status', 'tamanho']
    search_fields = ['quantidade', 'observacoes', 'categoria__nome', 'servico__nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-criado_em']
    list_per_page = 25

    fieldsets = (
        ('Informações do Item', {
            'fields': ('quantidade', 'categoria', 'servico', 'status', 'tamanho')
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
            'Manchado': 'Yellow',
            'Lavando': 'DarkOrange',
            'Limpo': 'royalgreen',
            'Retornou com mancha': 'MediumPurple',
        }
        cor = cores.get(obj.status, 'gray')
        return format_html(f'<span style="color: {cor}; font-weight: bold;">{obj.status}</span>')

    status_colorido.short_description = 'Status'
