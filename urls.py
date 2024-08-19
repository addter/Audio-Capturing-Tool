from django.urls import path
from .views import index, transcribe_audio

urlpatterns = [
    path('', index, name='index'),
    path('transcribe/', transcribe_audio, name='transcribe_audio'),
]
