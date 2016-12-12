import pytest
try:
    from unittest import mock
except ImportError:
    # python2
    import mock

from celery import Celery
from myr.client import Client, RemoteProcedureCaller


class TestClient:

    def test_init(self):
        client = Client()
        assert client.task_registry is None

    def test__send_discover(self):
        with mock.patch.object(
                Celery, 'send_task', return_value=None
        ) as mock_method:
            client = Client()
            client._send_discover()
            mock_method.assert_called_with(
                *client.DISCOVERY_ARGS,
                **client.DISCOVERY_KWARGS)
            client.discovery_args = ()
            client.discovery_kwargs = {}
            client._send_discover()
            mock_method.assert_called_with()

            client.discovery_args = ()
            client.discovery_kwargs = {'u': 2}
            client._send_discover()
            mock_method.assert_called_with(**{'u': 2})

    def test__process_discover(self):
        client = Client()
        discovered_tasks = {
            'remote.procedure': {
                'signature': {
                    'args': ['a'],
                    'defaults': None,
                    'varkw': None,
                    'varargs': None
                },
                'routing': {}
            }
        }
        registry = client._process_discover(discovered_tasks)
        assert len(registry) == 1

        discovered_tasks['remote.task'] = discovered_tasks['remote.procedure']
        registry = client._process_discover(discovered_tasks)
        assert len(registry) == 2

        registry['remote.task']['fn'](a=None)
        with pytest.raises(TypeError):
            registry['remote.procedure']['fn'](b=None)

    def test_discover(self):

        class AsyncResult:
            def get(self):
                return {
                    'remote.procedure': {
                        'signature': {
                            'args': ['a'], 'defaults': None,
                            'varkw': None, 'varargs': None
                        },
                        'routing': {}
                    },
                    'remote.task': {
                        'signature': {
                            'args': ['a', 'b'], 'defaults': None,
                            'varkw': None, 'varargs': None
                        },
                        'routing': {}
                    }
                }

        with mock.patch.object(
            Celery, 'send_task', return_value=AsyncResult()
        ):
            client = Client()
            client.discover()
        assert len(client.task_registry) == 2


class TestRemoteProcedureCaller:

    def test_getattr(self):
        class AsyncResult:
            def get(self):
                return {
                    'remote.procedure': {
                        'signature': {
                            'args': ['a'], 'defaults': None,
                            'varkw': None, 'varargs': None
                        },
                        'routing': {}
                    },
                    'remote.task': {
                        'signature': {
                            'args': ['a', 'b'], 'defaults': None,
                            'varkw': None, 'varargs': None
                        },
                        'routing': {}
                    }
                }
        with mock.patch.object(
            Celery, 'send_task', return_value=AsyncResult()
        ):
            client = Client()
            client.discover()
        assert len(client.task_registry) == 2

        remote = client.rpc.remote
        assert isinstance(remote, RemoteProcedureCaller)
        assert remote.client is client
        assert callable(client.rpc.remote.procedure)
        assert callable(remote.procedure)
        with pytest.raises(AttributeError):
            client.rpc.remote.nonexistent
        client.rpc.remote.task
