from django.urls import path
from . import views as main_views

urlpatterns = [
    path('register/', main_views.RegisterAPIView.as_view(), name="register"),
    path('questions/', main_views.QuestionAPIView.as_view(), name="question"),
    path('answer/', main_views.AnswerAPIView.as_view(), name="answer"),
    # path('result/', main_views.ResultAPIView.as_view(), name="result"),
]
 