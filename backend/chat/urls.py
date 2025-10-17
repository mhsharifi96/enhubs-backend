from chat.views import StartConversationAPIView,  ContinueConversationAPIView
from django.urls import path

urlpatterns = [
    path('start/', StartConversationAPIView.as_view(), name='chat-completion'),
    path('continue/', ContinueConversationAPIView.as_view(), name='chat-continue'),
]