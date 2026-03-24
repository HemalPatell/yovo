import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user      = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group = f'chat_{self.room_name}'

        # Reject unauthenticated users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Join the room group
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # ── Mark unread messages as read & broadcast "seen" to the room ──
        count = await self.mark_messages_read()
        if count > 0:
            # Tell the other user their messages were seen
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':    'messages_seen',
                    'seen_by': self.user.pk,
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    # ── Receive message from browser ──────────────────────────────────────────
    async def receive(self, text_data):
        data = json.loads(text_data)

        # ── Handle "mark_read" ping from browser (when tab gets focus) ────────
        if data.get('type') == 'mark_read':
            count = await self.mark_messages_read()
            if count > 0:
                await self.channel_layer.group_send(
                    self.room_group,
                    {
                        'type':    'messages_seen',
                        'seen_by': self.user.pk,
                    }
                )
            return

        # ── Handle normal chat message ─────────────────────────────────────────
        content     = data.get('message', '').strip()
        receiver_id = data.get('receiver_id')
        item_id     = data.get('item_id')

        if not content or not receiver_id or not item_id:
            return

        msg = await self.save_message(content, receiver_id, item_id)
        if not msg:
            return

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':        'chat_message',
                'message':     content,
                'sender_id':   self.user.pk,
                'sender_name': self.user.get_full_name() or self.user.username,
                'msg_id':      msg.pk,
                'timestamp':   msg.timestamp.strftime('%-I:%M %p'),
            }
        )

    # ── Broadcast chat message to room ────────────────────────────────────────
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':        'chat_message',
            'message':     event['message'],
            'sender_id':   event['sender_id'],
            'sender_name': event['sender_name'],
            'msg_id':      event['msg_id'],
            'timestamp':   event['timestamp'],
        }))

    # ── Broadcast "seen" event to room ────────────────────────────────────────
    async def messages_seen(self, event):
        await self.send(text_data=json.dumps({
            'type':    'messages_seen',
            'seen_by': event['seen_by'],
        }))

    # ── Database helpers ──────────────────────────────────────────────────────
    @database_sync_to_async
    def save_message(self, content, receiver_id, item_id):
        from django.contrib.auth.models import User
        from .models import Message, Item
        try:
            receiver = User.objects.get(pk=receiver_id)
            item     = Item.objects.get(pk=item_id)
            return Message.objects.create(
                sender   = self.user,
                receiver = receiver,
                item     = item,
                content  = content,
            )
        except Exception:
            return None

    @database_sync_to_async
    def mark_messages_read(self):
        """Mark all unread messages sent TO current user in this room as read.
           Returns how many were updated."""
        from .models import Message
        # Extract the two user IDs from the room name
        # room_name format: item_{item_pk}_users_{minId}_{maxId}
        try:
            parts   = self.room_name.split('_')
            item_id = int(parts[1])
            updated = Message.objects.filter(
                receiver = self.user,
                item_id  = item_id,
                is_read  = False,
            ).update(is_read=True)
            return updated
        except Exception:
            return 0