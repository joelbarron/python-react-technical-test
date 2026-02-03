from django.urls import path

from .views import TransactionAsyncProcessView, TransactionCreateView, TransactionListView

urlpatterns = [
    path("create", TransactionCreateView.as_view()),
    path("async-process", TransactionAsyncProcessView.as_view()),
    path("", TransactionListView.as_view()),
]
