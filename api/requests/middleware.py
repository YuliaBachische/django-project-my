import time

from django.http import HttpRequest
from datetime import datetime

from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):
    print('initial call')

    def middleware(request: HttpRequest):
        print('before get response')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('after get response')

        return response

    return middleware


class CountRequestsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.response_count = 0
        self.exception_count = 0
        self.request_time = {}

    def __call__(self, request: HttpRequest):
        time_wait = 5

        if not self.request_time:
            print('это первый запрос')
        else:
            if (round(time.time()) * 1) - self.request_time['time'] < time_wait and \
                    self.request_time['ip_address'] == request.META.get('REMOTE_ADDR'):
                print("Подождите более 5 секунд чтобы выполнить повторный запрос")
                return render(request, 'requests/throttling-error.html')

        self.request_time = {'time': round(time.time()) * 1, 'ip_address': request.META.get('REMOTE_ADDR')}

        self.requests_count += 1
        print('requests count: ', self.requests_count)
        response = self.get_response(request)
        self.response_count += 1
        print('response count: ', self.response_count)

        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exception_count += 1
        print('got', self.exception_count, "exceptions so far")
