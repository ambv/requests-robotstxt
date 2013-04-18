==================
requests-robotstxt
==================

.. image:: https://secure.travis-ci.org/ambv/requests-robotstxt.png
  :target: https://secure.travis-ci.org/ambv/requests-robotstxt

Currently just a proof of concept, the module strives to be an extension to
`requests <http://pypi.python.org/pypi/requests>`_ that brings automatic
support for robots.txt.

How to use
----------

Simply use ``RobotsAwareSession`` instead of the built-in ``requests.Session``.
If a resource is not allowed, a ``RobotsTxtDisallowed`` exception is raised.

How do I run the tests?
-----------------------

The easiest way would be to extract the source tarball and run::

  $ python test/test_robotstxt.py

Change Log
----------

0.1.0
~~~~~

* initial published version

Authors
-------

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_.
