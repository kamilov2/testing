import uuid
from rest_framework import views, status
from rest_framework.views import APIView
from rest_framework.response import Response
from . import models as main_models
from . import serializers as main_serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token





class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

    def get_paginated_data(self, queryset):
        self.page_size = self.get_page_size(self.request)
        self.page = self.paginate_queryset(queryset, self.request)
        if not self.page:
            return None, 0, 0
        return self.page.object_list, self.page.paginator.count, self.page.paginator.num_pages



class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        error_code = str(uuid.uuid4())[:15]
        try:
            name = request.data.get('name')
            phone_number = request.data.get('phone_number')
            if name is not None and phone_number is not None:
                if main_models.User.objects.filter(username=f'{name}{phone_number}').exists():
                    user = main_models.User.objects.get(username=f'{name}{phone_number}')
                    if hasattr(user, 'profile'):
                        profile = user.profile
                        result = main_models.UserTestResult.objects.get(user=profile)
                        result.score = 0
                        result.save()
                        return Response({'error': 'User with this username already exists.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                    
                user = main_models.User.objects.create(username=f'{name}{phone_number}')
                profile = main_models.Profile.objects.create(user=user, name=name, phone_number=phone_number)
                main_models.UserTestResult.objects.create(user=profile, test=main_models.Test.objects.first(), score=0)
                user.set_password(phone_number)
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'success': 'User created successfully.',
                                 'user_token': token.key
                                 }, status=status.HTTP_201_CREATED)
            else:
                error_log = main_models.ErrorLog.objects.create(
                    error_number=error_code,
                    error_message='Username or password is missing.',
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
                return Response({'error': 'An error occurred. Error ID: {}'.format(error_log.error_number)},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_log = main_models.ErrorLog.objects.create(
                error_number=error_code,
                error_message=str(e),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            return Response({'error': 'An error occurred. Error ID: {}'.format(error_log.error_number)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = main_serializers.QuestionSerializer

    def get(self, request):
        error_code = str(uuid.uuid4())[:15]

        try:
            first_test = main_models.Test.objects.first()
            if not first_test:
                return Response({'error': 'No tests available'}, status=status.HTTP_404_NOT_FOUND)

            queryset = main_models.Question.objects.filter(test=first_test).prefetch_related('answers')
            if not queryset.exists():
                return Response({'error': 'No questions available for the first test'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            error_log = main_models.ErrorLog.objects.create(
                error_number=error_code,
                error_message=str(e),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            return Response({'error': 'An error occurred. Error ID: {}'.format(error_log.error_number)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        error_code = str(uuid.uuid4())[:15]

        try:
            user = main_models.Profile.objects.get(user=request.user)
            answer_id = request.data.get('answer_id')

            if user is None or answer_id is None:
                return Response({'error': 'User or answer ID is missing'}, status=status.HTTP_400_BAD_REQUEST)

            answer = main_models.Answer.objects.get(id=answer_id)

            if answer is None or not answer.is_correct:
                return Response({'error': 'Invalid answer'}, status=status.HTTP_400_BAD_REQUEST)

            user_test_result, created = main_models.UserTestResult.objects.get_or_create(user=user)
            user_test_result.score += 1
            user_test_result.save()

            return Response({'success': 'Score updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            error_log = main_models.ErrorLog.objects.create(
                error_number=error_code,
                error_message=str(e),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            return Response({'error': 'An error occurred. Error ID: {}'.format(error_log.error_number)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class PhotoAPIView(views.APIView):
#     permission_classes = [AllowAny]
#     pagination_class = CustomPagination
#     serializer_class = main_serializers.PhotoSerializerc

#     def get(self, request):
#         paginator = self.pagination_class()
#         queryset = main_models.Photo.objects.all().order_by('-id')[:15]
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = self.serializer_class(result_page, many=True, context={'request': request})
#         return paginator.get_paginated_response(serializer.data)
    