crimp
=====

A JavaScript minifier command-line utility written fully in Python; uses
|calmjs.parse|_ as the underlying library.

.. image:: https://travis-ci.org/calmjs/crimp.svg?branch=1.0.1
    :target: https://travis-ci.org/calmjs/crimp
.. image:: https://ci.appveyor.com/api/projects/status/nmtjoh4mavbilgvo/branch/1.0.1?svg=true
    :target: https://ci.appveyor.com/project/metatoaster/crimp/branch/1.0.1
.. image:: https://coveralls.io/repos/github/calmjs/crimp/badge.svg?branch=1.0.1
    :target: https://coveralls.io/github/calmjs/crimp?branch=1.0.1

.. |crimp| replace:: ``crimp``
.. |calmjs.parse| replace:: ``calmjs.parse``
.. _calmjs.parse: https://pypi.python.org/pypi/calmjs.parse
.. |slimit| replace:: ``slimit``
.. _slimit: https://pypi.python.org/pypi/slimit


Introduction
------------

|crimp| serves as the front-end to |calmjs.parse|_.

Both these libraries had their origin in |slimit|_, a package that
provided a Python based solution for handling JavaScript code, which is
often used for situations where the usage of commonly used minifiers,
which are typically written in Node.js, is impractical from a pure
Python environment.  However, |slimit| had not been maintained for a
number of years.  As of 2017, with many issues that impacted the
correctness of the generated code remain outstanding, |calmjs.parse| was
forked from |slimit|, and |crimp| was created as a front end for the
former.


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
reveal the options that are available.

.. code::

    $ crimp --help
    usage: crimp [input_file [input_file ...]] [-h] [-O <output_path>] [-m] [-p]
                 [-s [<sourcemap_path>]] [--version] [-o] [--drop-semi]
                 [--indent-width n] [--encoding <codec>]

    positional arguments:
      input_file            path(s) to input file(s)

    optional arguments:
      -h, --help            show this help message and exit
      -O <output_path>, --output-path <output_path>
                            output file path
      -m, --mangle          enable all basic mangling options
      -p, --pretty-print    use pretty printer (omit for minify printer)
      -s [<sourcemap_path>], --source-map [<sourcemap_path>]
                            enable source map; filename defaults to
                            <output_path>.map, if identical to <output_path> it
                            will be written inline as a data url
      --version             show version information
      --indent-width n      indentation width for pretty printer
      --encoding <codec>    the encoding for file-based I/O; stdio relies on
                            system locale

    basic mangling options:
      -o, --obfuscate       obfuscate (mangle) names
      --drop-semi           drop unneeded semicolons (minify printer only)

Typically, the program will be invoked with a single or multiple input
files (if they are to be combined into a single file), and optionally
with the ``-m`` flag to denote that it is safe to have all the mangle
options enabled.

Please note that all input files *must* be listed before the flags, as
this forced grouping of all input files result in a less ambiguous
listing of files, given that there are flags for specifying target
output files, which will be overwritten without prompt.


Standard pretty/minified printing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To minify some file:

.. code::

    $ crimp project.js -O project.min.js

To minify some file with just variable name obfuscation:

.. code::

    $ crimp project.js -m -O project.min.js

Pretty printing the minified file back onto stdout:

.. code::

    $ crimp project.min.js -p

Reading input from stdin and writing out to a file.  Note that if a
SIGINT (typically Ctrl-C or Ctrl-Break), the output file will not be
opened for writing.

.. code::

    $ crimp -O demo.js

Source map generation
~~~~~~~~~~~~~~~~~~~~~

For source map generation, enable the ``-s`` flag.

.. code::

    $ crimp project.js -O project.min.js -s

The above will write out the source map file as ``project.min.js.map``,
and the reference to that (the ``sourceMappingURL``) will also be
appended to the output file as a comment.  To specify a specific
location, pass the name as a parameter.

.. code::

    $ crimp project.js -O project.min.js -s project.min.map

Inline source maps (where the ``sourceMappingURL`` is the data URL of
the base64 encoding of the JSON serialization of the source map) are
supported; these can be produced by supplying the argument with the same
name used for the output file, like so:

.. code::

    $ crimp project.js -O project.min.js -s project.min.js


Troubleshooting
---------------

Parsing a moderately sized file takes 10x as much time as uglifyjs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is due to the implementation done by |calmjs.parse| as a set of
generator functions that produce very minimum output, and that the
standard Python implementation has a very high overhead performance cost
for function calls.  The advantage with that approach is that maximum
flexibility can be achieved (due to the ease of which unparsing
workflows can be set up), while the drawback is obvious.


Contribute
----------

- Issue Tracker: https://github.com/calmjs/crimp/issues
- Source Code: https://github.com/calmjs/crimp


Legal
-----

The |crimp| package is copyright (c) 2017 Auckland Bioengineering
Institute, University of Auckland.  The |crimp| package is licensed
under the MIT license (specifically, the Expat License).
