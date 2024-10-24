from django.urls import path
from chat.views import *


urlpatterns = [
    path('', my_analysis, name='my-analysis'),
    path('new-analysis', new_analysis, name='new-analysis'),
    path('analyze/<str:pk>/', analyze, name='analyze'),
    # path('<str:pk>', chat, name='chat'),
    path('api/chat/<str:pk>/', chat, name='text-chat'),
    path('api/audio-chat/<str:pk>/', audio_chat, name='audio-chat'),
    path('api/get-file-data/<str:pk>/', get_file_data, name='get-file-data'),
]
