# example/urls.py
from django.urls import path

from .views import *


urlpatterns = [
    path('', lavanderia_flamboyant),
        path('item/<int:item_id>/ajustar_quantidade/', ajustar_quantidade_ajax, name='ajustar_quantidade_ajax'),

]