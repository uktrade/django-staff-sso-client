from unittest.mock import Mock

import pytest


@pytest.fixture
def mocked_oauth_client():
    return Mock()
