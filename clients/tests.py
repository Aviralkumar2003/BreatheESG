import pytest
from clients.models import Client

@pytest.mark.django_db
def test_create_client():
    client = Client.objects.create(name="Test Client")
    assert client.name == "Test Client"
    assert client.id is not None
