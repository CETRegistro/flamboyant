from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import *
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt # Use com cautela, ou remova se usar CSRF token no frontend

def lavanderia_flamboyant(request):
    inventario = Inventario.objects.all()
    return render(request, 'inventario.html', {'inventario': inventario})
# meuapp/views.py


@require_POST # Garante que a view só aceite requisições POST
@csrf_exempt # APENAS PARA TESTES OU SE VOCÊ GERENCIA O CSRF DE OUTRA FORMA NO FRONTEND. REMOVA PARA PRODUÇÃO COM CSRF_TOKEN DO DJANGO.
def criar_servico(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Verifica se é uma requisição AJAX
        item_id = request.POST.get('item_id')
        quantidade_servico = request.POST.get('retornou')
        dados_inventario = Inventario.objects.get(id=item_id).l
        print(dados_inventario.quantidade)
        """OrdemServico.objects.create(
                quantidade=quantidade_servico,
                categoria=minha_categoria,
                servico=meu_servico,
                status='Sujo',
                tamanho='Casal', # Ou outro tamanho válido de TAMANHO_CHOICES
                observacoes='Mancha leve na barra',
                retornou=0
            )"""
        
        try:
            
            return JsonResponse({'status': 'success', 'message': 'Item atualizado com sucesso!'})
        except OrdemServico.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item não encontrado.'}, status=404)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Valor de retorno inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro inesperado: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)