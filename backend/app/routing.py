from django.urls import path

from transactions.consumers import TransactionConsumer

websocket_urlpatterns = [
    # Single broadcast channel for all transaction updates.
    path("ws/transactions/", TransactionConsumer.as_asgi()),
]
