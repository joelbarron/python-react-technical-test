from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TransactionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Broadcast-only channel; no per-user auth in this demo.
        await self.channel_layer.group_add("transactions", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("transactions", self.channel_name)

    async def transaction_updated(self, event):
        await self.send_json({"event": "transaction.updated", "data": event["data"]})
