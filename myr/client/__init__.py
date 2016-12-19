# -*- coding: utf-8 -*-
'''
==========
myr.client
==========

Client module for ``myr-stack``
'''

from celery import current_app

from myr.client import fnutils
from myr.common import defaults as myr_defaults


class Client:

    DISCOVERY_ARGS = ('myr.discovery.discover', )
    DISCOVERY_KWARGS = {'queue': myr_defaults.discovery_queue}

    def __init__(
        self,
        app=None,
        send_task_options=None,
        discovery_args=None,
        discovery_kwargs=None
    ):
        self.app = app or current_app
        self.send_task_options = send_task_options or {}
        self.task_registry = None
        self.discovery_args = discovery_args or self.DISCOVERY_ARGS
        self.discovery_kwargs = discovery_kwargs or self.DISCOVERY_KWARGS

    def _send_discover(self):
        return self.app.send_task(
            *self.discovery_args, **self.discovery_kwargs)

    def _process_discover(self, discovered_tasks):
        registry = {}
        for task_name, task_def in discovered_tasks.items():
            task_def['fn'] = fnutils.function_from_signature(
                task_name.rsplit('.', 1)[-1], task_def['signature'])
            registry[task_name] = task_def
        return registry

    def discover(self):
        async_discovered = self._send_discover()
        self.task_registry = self._process_discover(async_discovered.get())

    def call_task(
        self, task_name, task_def,
        args=None, kwargs=None, **options
    ):
        # validate given arguments
        task_def['fn'](*args, **kwargs)
        options.update(task_def.get('routing', {}))
        return self.app.send_task(
            task_name, args=args, kwargs=kwargs, **options)

    @property
    def rpc(self):
        return RemoteProcedureCaller(
            client=self, base=(), options=self.send_task_options.copy())


class RemoteProcedureCaller:

    def __init__(self, client, base=(), options=None):
        self.client = client
        self.base = base
        self.options = options or {}

    def __getattr__(self, name):
        new_base = self.base + (name, )
        full_name = '.'.join(new_base)

        # If there is task with such a name return it's
        # preprepared task call
        if full_name in self.client.task_registry:
            options = self.options.copy()
            task_def = self.client.task_registry[full_name]

            # TODO: Copy __doc__ once it is available in the discovery
            def fn(*args, **kwargs):
                return self.client.call_task(
                    full_name, task_def,
                    args=args, kwargs=kwargs, **options)

            fn.__name__ = name
            return fn
        else:
            # If there is not task with such name:
            # - check if there is task which name starts with our full name and
            #   dot so on next __getattr__ call it eventualy can be called
            # - or raise AttributeError
            for task_name in self.client.task_registry:
                if task_name.startswith(full_name + '.'):
                    return self.__class__(
                        client=self.client,
                        base=new_base,
                        options=self.options)
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self, name))

    def __str__(self):
        return '<%s base=%r>' % (self.__class__.__name__, self.base)
