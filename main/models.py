from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Name: ')
    phone_number = models.CharField(max_length=100, verbose_name='Phone number: ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'{self.name} {self.phone_number}'

class Question(models.Model):
    text = models.TextField()

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        indexes = [
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return self.text

class Test(models.Model):
    title = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question)

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

class UserTestResult(models.Model):
    user = models.ForeignKey(Profile, related_name='test_results', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Test Result'
        verbose_name_plural = 'User Test Results'
        indexes = [
            models.Index(fields=['user', 'test']),
        ]

    @classmethod
    def get_user_test_scores(cls, user_id):
        return cls.objects.filter(user_id=user_id).select_related('test').values('test__title', 'score')

    @classmethod
    def get_user_test_count(cls, user_id):
        return cls.objects.filter(user_id=user_id).count()

    @classmethod
    def get_user_test_avg_score(cls, user_id):
        return cls.objects.filter(user_id=user_id).aggregate(models.Avg('score'))

class ErrorsDBManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('errors_db')

class ErrorLog(models.Model):
    error_number = models.CharField(max_length=100)
    error_message = models.TextField()
    user_agent = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"

    objects = ErrorsDBManager()

    def __str__(self):
        return self.error_number
