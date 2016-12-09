
=============
myr.client
=============

.. image:: https://travis-ci.org/Vnet-as/myr-client.svg?branch=master
   :target: https://travis-ci.org/Vnet-as/myr-client


.. image:: https://codecov.io/gh/Vnet-as/myr-client/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Vnet-as/myr-client


Client for ``myr-stack``


Installation
============

Development
-----------

Create `virtualenv <https://virtualenv.pypa.io/en/stable/>`_ and activate
it, then proceed to install ``myr-client`` for development:

.. code-block:: bash

    $ git clone https://github.com/Vnet-as/myr-client.git
    $ cd myr-client
    $ pip install -e .


Usage
=====

.. code-block:: python

    import celeryconf
    from celery import Celery

    app = Celery()
    app.config_from_object(celeryconf)

    from myr.client import Client

    client = Client()

    # conntact myr-discovery service to get the task/procedures definitions
    client.discover()

    # Now if ``invoicing.tasks.add_item`` was discovered in previous call
    # we can call it by ``client.rpc``
    client.rpc.invoicing.tasks.add_item(*args, **kwargs)
