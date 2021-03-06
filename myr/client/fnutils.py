# -*- coding: utf-8 -*-
'''
==================
myr.client.fnutils
==================
'''

import inspect

FUNCTION_SIGNATURE_FMT = '''\
def {name}({arg_fmt}):
    pass
'''


def function_from_signature(name, signature, fmt=FUNCTION_SIGNATURE_FMT):
    namespace = {}
    exec(
        FUNCTION_SIGNATURE_FMT.format(
            name=name,
            arg_fmt=formatargspec(**signature)
        ),
        namespace,
    )
    return namespace[name]


def formatargspec(**spec):
    # handle inspect.getargspec (ArgSpec format)
    if 'keywords' in spec:
        spec['varkw'] = spec.pop('keywords')

    if hasattr(inspect, 'formatargspec'):
        return inspect.formatargspec(**spec)[1:-1]
    else:
        # Stolen from celery.utils.functional
        if spec['defaults']:
            split = len(spec['defaults'])
            positional = spec['args'][:-split]
            optional = list(zip(spec['args'][-split:], spec['defaults']))
        else:
            positional, optional = spec['args'], []
            varkw = spec['varkw']
            varargs = spec['varargs']
        return ', '.join(filter(None, [
            ', '.join(positional),
            ', '.join('{0}={1}'.format(k, v) for k, v in optional),
            '*{0}'.format(varargs) if varargs else None,
            '**{0}'.format(varkw) if varkw else None,
        ]))
