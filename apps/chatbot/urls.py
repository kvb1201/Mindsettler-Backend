from django.urls import path
from .views import ChatbotIntentView

urlpatterns = [
    path("intent/", ChatbotIntentView.as_view()),
]