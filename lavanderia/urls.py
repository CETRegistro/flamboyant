# example/urls.py
from django.urls import path

from .views import *


urlpatterns = [
    path('', lavanderia_flamboyant),
    path('criar_servico/', criar_servico, name='criar_servico'),


]