from rest_framework import serializers
from . import models as main_models

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = main_models.Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = main_models.Question
        fields = ['id', 'text', 'answers']
