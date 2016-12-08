
from myr.client import Client


class TestClient:

    def test_init(self):
        client = Client()
        assert client.task_registry is None
