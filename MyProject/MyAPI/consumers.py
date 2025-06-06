import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notifications
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('action') == 'mark_as_read':
            noti_id = data.get('noti_id')
            await self.mark_as_read(noti_id)

            # Đếm lại số chưa đọc
            unread_count = await self.get_unread_count()

            # Phản hồi lại client
            await self.send(text_data=json.dumps({
                'action': 'read_confirmed',
                'noti_id': noti_id,
                'unread_count': unread_count
            }))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def mark_as_read(self, noti_id):
        try:
            noti = Notifications.objects.get(noti_id=noti_id, user_id=self.user_id)
            noti.read_status = True
            noti.save()
        except Notifications.DoesNotExist:
            pass

    @database_sync_to_async
    def get_unread_count(self):
        return Notifications.objects.filter(user_id=self.user_id, read_status=False).count()