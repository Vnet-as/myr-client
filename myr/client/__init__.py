# -*- coding: utf-8 -*-
'''
==========
myr.client
==========

Client module for ``myr-stack``
'''

from celery import current_app

from myr.client import fnutils


class Client:

    DISCOVERY_DEFAULT_ARGS = ('myr.discovery.discover', )
    DISCOVERY_DEFAULT_KWARGS = {}

    def __init__(self, app=None):
        self.app = app or current_app
        self.task_registry = None

    def _send_discover(self, args=None, kwargs=None):
        args = self.DISCOVERY_DEFAULT_ARGS if args is None else args
        kwargs = self.DISCOVERY_DEFAULT_KWARGS if kwargs is None else kwargs
        return self.app.send_task(*args, **kwargs)

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
