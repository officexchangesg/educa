from django.urls import re_path
from . import consumers
websocket_urlpatterns = [
    # .as_asgi() to address the issue of followings
    # TypeError: __call__() missing 1 required positional argument: 'send'
    # WebSocket DISCONNECT /ws/chat/room/1/
    re_path(r'ws/chat/room/(?P<course_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
