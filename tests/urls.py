import django
from django.http import HttpResponse
from django.views import View

try:
    from django.urls import path, include
except ImportError:
    from django.conf.urls import url, include


class HomePageView(View):
    def get(self, request):
        return HttpResponse('Hey!')


if django.VERSION[0] >= 2:
    urlpatterns = [
        path('auth/', include(
            'authbroker_client.urls',
            namespace='authbroker'
        )),
        path('', HomePageView.as_view(), name='home')
    ]
else:
    urlpatterns = [
        url('^auth/', include(
            'authbroker_client.urls',
            namespace='authbroker'
        )),
        url(r'^$', HomePageView.as_view(), name='home')
    ]
