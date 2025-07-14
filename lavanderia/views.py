from django.shortcuts import render
from .models import Item
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Item

def lavanderia_flamboyant(request):
    itens = Item.objects.all()
    return render(request, 'lavanderia.html', {'itens': itens})

@require_POST
def ajustar_quantidade_ajax(request, item_id):
    delta = int(request.POST.get('delta', 0))
    item = get_object_or_404(Item, id=item_id)

    nova_quantidade = item.quantidade + delta
    nova_quantidade = max(1, min(nova_quantidade, 999))

    if nova_quantidade != item.quantidade:
        item.quantidade = nova_quantidade
        item.save()
        status = 'ok'
    else:
        status = 'no_change'

    return JsonResponse({
        'status': status,
        'nova_quantidade': item.quantidade,
        'item_id': item.id,
    })
