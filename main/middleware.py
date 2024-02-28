# import hashlib
# from django.http import HttpResponseForbidden
# from .models import Profile
# from django.shortcuts import render



# class UniqueDeviceMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         device_info = f"{request.META.get('HTTP_USER_AGENT')}_{request.META.get('REMOTE_ADDR')}"
#         device_id = hashlib.sha256(device_info.encode()).hexdigest()

#         if not request.session.get('device_id'):
#             profile, created = Profile.objects.get_or_create(device_id=device_id, name=device_info)
#             request.session['device_id'] = device_id

#             if created:
#                 print(f"New profile created: {profile}")
#             else:
#                 print(f"Existing profile retrieved: {profile}")

#         request.device_id = device_id
#         response = self.get_response(request)
#         return response



# class BlockOtherDevicesMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):       
#         current_device_id = getattr(request, 'device_id', None)
#         profile = Profile.objects.filter(device_id=current_device_id).first()

#         if profile and profile.permission:  
#             response = self.get_response(request)
#             return response
#         else:
#             return HttpResponseForbidden('Siz admin tomonidan bloklangan usersiz!')


# middleware.py



import os
import time
import gzip
from io import BytesIO
from datetime import datetime
from django.middleware.csrf import CsrfViewMiddleware
from django.db import DatabaseError
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class DeleteOldMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.delete_old_files()
        response = self.get_response(request)
        return response

    def delete_old_files(self):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                filepath = os.path.join(root, file)
                if os.stat(filepath).st_mtime < time.time() - 10:
                    os.remove(filepath)

class RequestTimeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = datetime.now()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = datetime.now() - request.start_time
            print(f"Request to {request.path} took {duration.total_seconds()} seconds. Project name: Pyblog. Domen: https://pyblog.uz")
        return response
    

class SecurityMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        try:
            self.process_request(request)

            if any(char in request.path for char in [';', '--']):
                return HttpResponseBadRequest("Invalid characters detected in request.")
        except DatabaseError:
            return HttpResponseBadRequest("Database error occurred.")

        return None



class GZipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            if 'text' in response.get('Content-Type', ''):
                gzip_buffer = BytesIO()
                with gzip.GzipFile(mode='wb', fileobj=gzip_buffer) as gzip_file:
                    gzip_file.write(response.content)
                response.content = gzip_buffer.getvalue()
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(len(response.content))

        return response
    
from django.http import HttpResponse
from collections import defaultdict
from time import time

class RateLimitMiddleware:
    def __init__(self, get_response, capacity=100, refill_interval=60):
        self.get_response = get_response
        self.capacity = capacity  
        self.refill_interval = refill_interval 
        self.tokens = defaultdict(lambda: (self.capacity, time()))

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        tokens, last_refill_time = self.tokens[ip]

        current_time = time()
        if current_time - last_refill_time > self.refill_interval:
            self.tokens[ip] = (self.capacity, current_time)
            tokens = self.capacity

        if tokens > 0:
            self.tokens[ip] = (tokens - 1, last_refill_time)
            return self.get_response(request)
        else:
            return HttpResponse('Rate limit exceeded', status=429)