import pytest
from django.urls import reverse


@pytest.mark.parametrize('view_name,expected_url', [
    (
        'authbroker:login',
        '/auth/login/'
    ),
    (
        'authbroker:callback',
        '/auth/callback/'
    )
])
def test_reverse_urls(view_name, expected_url):
    assert reverse(view_name) == expected_url
