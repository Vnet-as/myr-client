# -*- coding: utf-8 -*-

import sys
import inspect

import myr.client.fnutils as fnutils

IS_PY3 = sys.version_info[0] == 3


class TestArgsSignature:

    def _test_args_signature_str_from_spec(self, fn, sig, only_full=False):
        if not only_full:
            spec = inspect.getargspec(fn)
            assert fnutils.formatargspec(spec._asdict()) == sig
        if IS_PY3:
            spec = inspect.getfullargspec(fn)
            assert fnutils.formatargspec(spec._asdict()) == sig

    def test_simple(self):
        def fn(a):
            pass
        sig = 'a'
        self._test_args_signature_str_from_spec(fn, sig)

        def fn(a, b):
            pass
        sig = 'a, b'
        self._test_args_signature_str_from_spec(fn, sig)

    def test_default_values(self):
        def fn(a, b=None):
            pass
        sig = 'a, b=None'
        self._test_args_signature_str_from_spec(fn, sig)

        def fn(a, b=None, **kwargs):
            pass
        sig = 'a, b=None, **kwargs'
        self._test_args_signature_str_from_spec(fn, sig)

        if IS_PY3:
            from tests._fn3 import kwonly_fn
            self._test_args_signature_str_from_spec(
                kwonly_fn, kwonly_fn.sig, only_full=True)

    def test_args_kwargs(self):
        def fn(a, b, *args, **kwargs):
            pass
        sig = 'a, b, *args, **kwargs'
        self._test_args_signature_str_from_spec(fn, sig)
