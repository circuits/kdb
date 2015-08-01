.. _#circuits: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _Docker: https://www.docker.com/
.. _Docker Compose: https://github.com/docker/compose
.. _autodock-paas: https://github.com/prologic/autodock-paas
.. _FreeNode IRC Network: http://freenode.net

kdb is a small pluggable IRC Bot framework utilizing the
`circuits <http://circuitsframework.com/>`_
Python Application Framework.

kdb was one of the first "test" applications written
in circuits and is still maintained and kept up-to-date
with new features and changes in circuits.

You may use kdb as a framework to build your own projects that
use the IRC protocol. kdb itself comes with a suite of useful
plugins and features. If you'd like to see it in action, feel
free to get in touch with the developer
`James Mills <http://prologic.shortcircuit.net.au/>`_ (*prologic*)
on the FreeNode IRC Network who resides in the #circuits channel.

kdb was created by and is primarily maintained by
`James Mills <http://prologic.shortcircuit.net.au/>`_


- `Website <https://github.com/prologic/kdb/>`_
- `Issues <https://github.com/prologic/kdb/issues>`_
- `#circuits`_ on the `FreeNode IRC Network`_


Installation
------------

::
    
    $ pip install kdb


Usage
-----

::
    
    $ kdb irc.freenode.net

For other options::
    
    $ kdb --help


Installation and Usage on Docker
--------------------------------

kdb is now `Docker`_ ready and can be run with::
    
    $ docker run -d -p 8000:8000 -v $(pwd)/etc:/etc/kdb prologic/kdb --config=/etc/kdb/kdb.ini

.. note:: Be sure to edit ``etc/kdb.ini`` or change the above line
          to suit your needs mounting the configuration directory
          from another path on your host.

Alternatively you can spin up kdb using `Docker`_ and `Docker Compose`_::
    
    docker-compose up -d

Using the following `docker-compose.yml <https://github.com/prologic/kdb/tree/master/docker-compose.yml>`_::

    kdb:
        image: prologic/kdb
        volumes:
            - ${PWD}/etc:/etc/kdb
        environment:
            - PORT=8000
            - VIRTUALHOST=kdb.vz1.bne.shortcircuit.net.au
        command: --config=/etc/kdb/kdb.ini
        restart: always

This also conveniently uses `autodock-paas`_ to setup virtualhost routing for
the web interface for the domain: http://kdb.vz1.bne.shortcircuit.net.au/

Plugins
-------

kdb has a full complementary set of plugins available.

For a list of available plugins, see:

https://github.com/prologic/kdb/tree/master/kdb/plugins/


You may install the latest `Development Version <https://github.com/prologic/kdb/archive/master.zip#egg=kdb-dev>`_ via::
    
    $ pip install kdb==dev
