# example/urls.py
from django.urls import path
from django.conf.urls.static import static # Importe static
from django.conf import settings # Importe settings


from .views import *


urlpatterns = [
    path('', inventario_flamboyant, name='inventario_lista'),
    path('criar_servico/', criar_servico, name='criar_servico'),
    path('ordens_servico/<int:categoria_id>/', ordens_servico_por_categoria, name='ordens_servico_por_categoria'),
    path('retornar_ao_inventario/', retornar_ao_inventario, name='retornar_ao_inventario'), # Nova URL
    
    path('atualizar-ordem-servico-campo/', atualizar_ordem_servico_campo, name='atualizar_ordem_servico_campo'),
    path('relatorio-totais/', total_itens_por_categoria_tamanho, name='relatorio_totais'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
