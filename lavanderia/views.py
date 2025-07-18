from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt # Use com cautela, ou remova se usar CSRF token no frontend
from django.db import transaction
from django.core.exceptions import ValidationError


def inventario_flamboyant(request):
    inventario = Inventario.objects.all()
    servicos = Servico.objects.all() # Busca todos os serviços
    return render(request, 'inventario.html', {'inventario': inventario,'servicos':servicos})

def servicos_flamboyant(request):
    servicos = OrdemServico.objects.all()
    return render(request, 'lavanderia.html', {'servicos': servicos})


def ordens_servico_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    ordens_servico = OrdemServico.objects.filter(categoria=categoria).order_by('-criado_em')

    context = {
        'categoria': categoria,
        'ordens_servico': ordens_servico,
    }
    return render(request, 'ordens_servico_categoria.html', context)


@csrf_exempt
@require_POST
def retornar_ao_inventario(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            ordem_servico_id = request.POST.get('ordem_servico_id')
            quantidade_retorno = int(request.POST.get('quantidade_retorno'))

            with transaction.atomic(): # Garante atomicidade da operação
                ordem_servico = get_object_or_404(OrdemServico, pk=ordem_servico_id)

                # Verifica se a quantidade a retornar é válida
                # A quantidade retornada não pode exceder a quantidade total da OS menos o que já retornou
                if quantidade_retorno <= 0 or quantidade_retorno > (ordem_servico.quantidade - ordem_servico.retornou):
                    raise ValidationError('Quantidade de retorno inválida ou excede o disponível na ordem de serviço.')

                # Atualiza a quantidade "retornou" na Ordem de Serviço
                ordem_servico.retornou += quantidade_retorno
                
                # --- Adição da lógica de status ---
                if ordem_servico.retornou == ordem_servico.quantidade:
                    ordem_servico.status = 'Operação concluída' # Altera o status
                # --- Fim da lógica de status ---

                ordem_servico.save(update_fields=['retornou', 'status']) # Salva os campos modificados

                # Encontra o item de inventário correspondente
                inventario_item = Inventario.objects.get(
                    categoria=ordem_servico.categoria,
                    tamanho=ordem_servico.tamanho
                )

                # Soma a quantidade de volta ao inventário
                inventario_item.quantidade += quantidade_retorno
                inventario_item.save(update_fields=['quantidade']) # Salva apenas o campo modificado

                return JsonResponse({'status': 'success', 'message': f'{quantidade_retorno} itens retornados com sucesso.'})

        except OrdemServico.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ordem de serviço não encontrada.'}, status=404)
        except Inventario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item de inventário correspondente não encontrado. Verifique a categoria e o tamanho.'}, status=404)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Quantidade de retorno inválida.'}, status=400)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválido.'}, status=400)


@csrf_exempt
@require_POST
def criar_servico(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            item_id = request.POST.get('item_id')
            quantidade_servico = int(request.POST.get('quantidade_servico'))
            servico_id = request.POST.get('servico_id')

            inventario_item = Inventario.objects.get(id=item_id)
            servico_obj = Servico.objects.get(id=servico_id)

            # Crie a nova OrdemServico
            nova_ordem = OrdemServico(
                quantidade=quantidade_servico,
                categoria=inventario_item.categoria,
                servico=servico_obj,
                status='Sujo', # Status inicial
                tamanho=inventario_item.tamanho,
                observacoes=f'Ordem criada a partir do inventário ID: {item_id}'
            )

            nova_ordem.full_clean() # Valida o modelo antes de salvar
            nova_ordem.save() # Salva e aciona o ajuste de inventário

            return JsonResponse({'status': 'success', 'message': 'Ordem criada e inventário atualizado.'})

        except Inventario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item de inventário não encontrado.'}, status=404)
        except Servico.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tipo de serviço não encontrado.'}, status=404)
        except ValidationError as e:
            # Retorna os erros de validação do modelo
            return JsonResponse({'status': 'error', 'message': e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Quantidade ou ID de serviço inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)


# --- NOVA VIEW PARA ATUALIZAR CAMPO ---
@csrf_exempt
@require_POST
def atualizar_ordem_servico_campo(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            ordem_servico_id = request.POST.get('ordem_servico_id')
            campo = request.POST.get('campo')
            valor = request.POST.get('valor')

            ordem_servico = get_object_or_404(OrdemServico, pk=ordem_servico_id)

            # Valida qual campo está sendo atualizado para evitar atualização de campos não intencionais
            if campo == 'observacoes':
                setattr(ordem_servico, campo, valor)
                ordem_servico.save(update_fields=[campo]) # Salva apenas o campo modificado
                return JsonResponse({'status': 'success', 'message': f'Campo "{campo}" atualizado com sucesso.', 'novo_valor': valor})
            else:
                return JsonResponse({'status': 'error', 'message': 'Campo não permitido para edição via AJAX.'}, status=400)

        except OrdemServico.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ordem de serviço não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)





# --- NOVA VIEW: total_itens_por_categoria_tamanho ---
def total_itens_por_categoria_tamanho(request):
    """
    Calcula o total de itens (Inventário + Ordens de Serviço)
    agrupados por Categoria e Tamanho.
    """
    resultados = {}

    # 1. Obter todas as Categorias e Tamanhos distintos de Inventário e OrdemServico
    # Isso garante que pegamos todas as combinações existentes
    categorias_tamanhos = set()
    for item in Inventario.objects.values('categoria__nome', 'tamanho').distinct():
        categorias_tamanhos.add((item['categoria__nome'], item['tamanho']))
    for item in OrdemServico.objects.values('categoria__nome', 'tamanho').distinct():
        categorias_tamanhos.add((item['categoria__nome'], item['tamanho']))

    for categoria_nome, tamanho_item in sorted(list(categorias_tamanhos)):
        # Consulta Inventario
        quantidade_inventario = Inventario.objects.filter(
            categoria__nome=categoria_nome,
            tamanho=tamanho_item
        ).aggregate(total=Sum('quantidade'))['total'] or 0

        # Consulta OrdemServico
        # Aqui, sumamos a 'quantidade' original da OS e subtraímos a 'retornou'
        # para obter a quantidade que ainda está "em serviço" ou "fora do inventário"
        quantidade_ordem_servico = OrdemServico.objects.filter(
            categoria__nome=categoria_nome,
            tamanho=tamanho_item
        ).aggregate(total_os=Sum(F('quantidade') - F('retornou')))['total_os'] or 0
        
        # O total é a soma do inventário com o que está em ordens de serviço
        total_geral = quantidade_inventario + quantidade_ordem_servico

        if categoria_nome not in resultados:
            resultados[categoria_nome] = {}
        
        resultados[categoria_nome][tamanho_item] = {
            'inventario': quantidade_inventario,
            'em_servico': quantidade_ordem_servico,
            'total_geral': total_geral
        }

    # Você pode renderizar um template ou retornar um JsonResponse
    # Para fins de demonstração, vou retornar um JsonResponse
    return render(request, 'relatorio_total_itens.html', {'resultados': resultados})
