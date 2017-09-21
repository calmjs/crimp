crimp
=====

A JavaScript minifier command-line utility written fully in Python; uses
|calmjs.parse|_ as the underlying library.

.. image:: https://travis-ci.org/calmjs/crimp.svg?branch=master
    :target: https://travis-ci.org/calmjs/crimp
.. image:: https://ci.appveyor.com/api/projects/status/_/branch/master?svg=true
    :target: https://ci.appveyor.com/project/metatoaster/crimp/branch/master
.. image:: https://coveralls.io/repos/github/calmjs/crimp/badge.svg?branch=master
    :target: https://coveralls.io/github/calmjs/crimp?branch=master

.. |crimp| replace:: ``crimp``
.. |calmjs.parse| replace:: ``calmjs.parse``
.. _calmjs.parse: https://pypi.python.org/pypi/calmjs.parse
.. |slimit| replace:: ``slimit``
.. _slimit: https://pypi.python.org/pypi/slimit


Introduction
------------

|crimp| serves as the front-end to |calmjs.parse|_ as there are
situations where the usage and installation of commonly used minifiers,
which are often written in Node.js, is not possible.  While the Python
package, |slimit|_, already exists to provide a Python based JavaScript
minifier, parser and lexer, there are many outstanding issues affecting
it that were never resolved as of 2017, and so |calmjs.parse| was forked
from |slimit| and this package was created as a way to rectify the
situation.


Installation
------------

The following command may be executed to source the latest stable
version of |crimp| wheel from PyPI for installation into the current
Python environment.

.. code:: sh

    $ pip install crimp


Usage
-----

As |crimp| is a package that offers a command of the same name,
executing the command after installation with the ``--help`` flag will
reveal the options

.. code:: sh

    $ crimp --help

Pretty/minified printing
~~~~~~~~~~~~~~~~~~~~~~~~

XXX TODO

Source map generation
~~~~~~~~~~~~~~~~~~~~~

XXX TODO


Troubleshooting
---------------

XXX TODO


Contribute
----------

- Issue Tracker: https://github.com/calmjs/crimp/issues
- Source Code: https://github.com/calmjs/crimp


Legal
-----

The |crimp| package is copyright (c) 2017 Auckland Bioengineering
Institute, University of Auckland.  The |crimp| package is licensed
under the MIT license (specifically, the Expat License).
