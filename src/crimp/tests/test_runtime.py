# -*- coding: utf-8 -*-
"""
Runtime tests
"""

import unittest
import base64
import json
import sys
import io
import os

from os import chdir
from os import getcwd
from os.path import exists
from os.path import join
from tempfile import mktemp
from tempfile import mkdtemp
from textwrap import dedent
from shutil import rmtree
from subprocess import Popen
from subprocess import PIPE

from crimp import runtime


class StringIO(io.StringIO):
    def close(self):
        # don't actually close the stream
        self.called_close = True


class BytesIO(io.BytesIO):
    def close(self):
        # don't actually close the stream
        self.called_close = True


def TextIO(*a):
    # this is typically used for stderr, when the underlying libraries
    # (most notably logging) require that the stream is of an exact type
    # due to the datatypes that it uses in Python 2.
    return BytesIO(*a) if str is bytes else StringIO(*a)


class RuntimeTestCase(unittest.TestCase):

    def mkdtemp(self):
        target = mkdtemp()
        self.addCleanup(rmtree, target)
        return target

    def chdir(self, path):
        self.addCleanup(chdir, getcwd())
        chdir(path)

    def reset_io(self):
        sys.stdin, sys.stdout, sys.stderr = (
            self.old_stdin, self.old_stdout, self.old_stderr)

    def stub_stdio_bytes(self):
        self.old_stderr, sys.stderr = sys.stderr, TextIO()
        self.old_stdout, sys.stdout = sys.stdout, BytesIO()
        self.old_stdin, sys.stdin = sys.stdin, BytesIO()

        sys.stderr.name = '<stderr>'
        sys.stdout.name = '<stdout>'
        sys.stdin.name = '<stdin>'
        # only if BytesIO, which is no longer always the case
        # sys.stderr.encoding = self.old_stderr.encoding
        sys.stdout.encoding = self.old_stdout.encoding
        sys.stdin.encoding = self.old_stdin.encoding
        self.addCleanup(self.reset_io)

    def stub_stdio_text(self):
        self.old_stderr, sys.stderr = sys.stderr, TextIO()
        self.old_stdout, sys.stdout = sys.stdout, StringIO()
        self.old_stdin, sys.stdin = sys.stdin, StringIO()
        self.addCleanup(self.reset_io)

    def stub_stdio(self):  # pragma: no cover
        if str is bytes:
            self.stub_stdio_bytes()
        else:
            self.stub_stdio_text()

    def test_resolve_prog(self):
        old_path = os.environ.get('PATH')

        def cleanup():
            os.environ['PATH'] = old_path

        self.addCleanup(cleanup)

        root = mktemp()
        os.environ['PATH'] = root
        self.assertEqual('prog', runtime.resolve_prog(join(root, 'prog')))
        alt = join(mktemp(), 'prog')
        self.assertEqual(alt, runtime.resolve_prog(alt))
        self.assertEqual('prog', runtime.resolve_prog(join(root, 'prog')))
        self.assertIn('-m crimp', runtime.resolve_prog(
            join(root, 'prog', '__main__.py')))

    def test_argparser_basic(self):
        parser = runtime.create_argparser('crimp')
        p = parser.parse_args([])
        self.assertEqual([], p.inputs)
        self.assertIsNone(p.output)

    def test_argparser_basic_inputs(self):
        parser = runtime.create_argparser('crimp')
        self.assertEqual(['some.js'], parser.parse_args(
            ['some.js']).inputs)
        self.assertEqual(['some.js', 'other.js'], parser.parse_args(
            ['some.js', 'other.js', '-m']).inputs)
        self.assertEqual(['some.js'], parser.parse_args(
            ['some.js']).inputs)
        self.assertEqual(['some.js', 'other.js'], parser.parse_args(
            ['some.js', 'other.js', '-m']).inputs)

        # this should error
        parser.parse_args(['-m', 'some.js', 'other.js'])

    def test_argparser_sourcemap_arg(self):
        parser = runtime.create_argparser('crimp')
        p = parser.parse_args(['-m'])
        self.assertIsNone(p.source_map)

        p = parser.parse_args(['-s', 'some.map'])
        self.assertEqual('some.map', p.source_map)

        parser = runtime.create_argparser('crimp')
        p = parser.parse_args(['-s', '-m'])
        self.assertEqual('', p.source_map)

    def test_argparser_trailing_inputs(self):
        self.stub_stdio()
        # yes, this results in a failure
        with self.assertRaises(SystemExit) as e:
            runtime.parse_args('crimp', 'some.js', 'other.js', '-m', 'path')

        self.assertEqual(e.exception.args[0], 2)

        # however, the usage message MUST show that input_file option
        # lies BEFORE every other options, which the default help
        # formatter does NOT do... so a custom formatter is needed and
        # this tests that rendering.

        usage = sys.stderr.getvalue()
        self.assertTrue(usage.startswith('usage: crimp [input_file ['))

        # The main reason for forcing the input_files to be _before_ the
        # flag is to offer some protection against the following patter,
        # where the user forgot to put dest.js after -O and somehow also
        # have two source files they wrote be part of the command line.
        # The naive interpretation through the argparser will result in
        # source1.js be a destination and thus be overwritten.
        with self.assertRaises(SystemExit) as e:
            runtime.parse_args('crimp', '-O', 'source1.js', 'source2.js')

        self.assertEqual(e.exception.args[0], 2)

    def test_main_keyboard_interrupt_source_file_dest_file(self):
        self.stub_stdio()

        def keyboard_break():
            raise KeyboardInterrupt

        sys.stdin.read = keyboard_break

        root = self.mkdtemp()
        dest = join(root, 'source.js')
        # This will at least stop the case where only one file being
        # listed as the outfile without any input from overwriting a
        # potential source file.
        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '-O', dest)

        # the exit code for keyboard interrupted.
        self.assertEqual(e.exception.args[0], 130)
        # ensure destination file is NOT created (which could be an
        # accidentally specified source file that could have been
        # unintentionally be overwritten otherwise).
        self.assertFalse(exists(dest))

    def test_main_basic_run_source_file(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        self.stub_stdio()
        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', source)

        self.assertEqual(e.exception.args[0], 0)
        self.assertEqual('var foo="bar";', sys.stdout.getvalue())

    def test_main_basic_run_source_file_dest_file(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        dest = join(root, 'dest.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', source, '-O', dest)

        self.assertEqual(e.exception.args[0], 0)

        with open(dest) as fd:
            self.assertEqual('var foo="bar";', fd.read())

    def test_main_basic_run_source_file_sourcemap_stdout(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        self.stub_stdio()
        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', source, '-s')

        self.assertEqual(e.exception.args[0], 0)
        self.assertIn(
            'var foo="bar";\n//# sourceMappingURL=data:application/json',
            sys.stdout.getvalue())

    def test_main_basic_run_source_file_sourcemap_implied(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        dest = join(root, 'dest.js')
        dest_map = join(root, 'dest.js.map')
        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', source, '-O', dest, '-s')

        self.assertEqual(e.exception.args[0], 0)

        with open(dest) as fd:
            self.assertEqual(
                'var foo="bar";\n//# sourceMappingURL=dest.js.map\n',
                fd.read(),
            )

        # implied sourcemap file should be created at the same level at
        # the same dirname.
        with open(dest_map) as fd:
            mapping = json.loads(fd.read())
            self.assertEqual({
                'version': 3,
                'file': 'dest.js',
                'mappings': 'AAAA,OAAQ,CAAE',
                'names': [],
                'sources': ['source.js'],
            }, mapping)

    def test_main_basic_run_source_file_sourcemap_reldir(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        self.chdir(root)
        dest = join(root, 'dest.js')
        # manually specified name
        dest_map = join(root, 'dest.map')
        with self.assertRaises(SystemExit) as e:
            runtime.main(
                'crimp', 'source.js', '-O', 'dest.js', '-s', 'dest.map')

        self.assertEqual(e.exception.args[0], 0)

        with open(dest) as fd:
            self.assertEqual(
                'var foo="bar";\n//# sourceMappingURL=dest.map\n',
                fd.read(),
            )

        # implied sourcemap file should be created at the same level at
        # the same dirname.
        with open(dest_map) as fd:
            mapping = json.loads(fd.read())
            self.assertEqual({
                'version': 3,
                'file': 'dest.js',
                'mappings': 'AAAA,OAAQ,CAAE',
                'names': [],
                'sources': ['source.js'],
            }, mapping)

    def test_main_basic_inline_sourcemap(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = "bar";')

        self.chdir(root)
        dest = join(root, 'dest.js')
        with self.assertRaises(SystemExit) as e:
            runtime.main(
                'crimp', 'source.js', '-O', 'dest.js', '-s', 'dest.js')

        self.assertEqual(e.exception.args[0], 0)

        with open(dest) as fd:
            raw = fd.read()

        self.assertIn(
            'var foo="bar";\n//# sourceMappingURL=data:application/json',
            raw,
        )

        self.assertEqual({
            "version": 3,
            "sources": ["source.js"],
            "names": [],
            "mappings": "AAAA,OAAQ,CAAE",
            "file": "dest.js"
        }, json.loads(base64.b64decode(
            raw.splitlines()[-1].split(',')[-1].encode('utf8')
        ).decode('utf8')))

    def test_pretty_print_stdio(self):
        self.stub_stdio()
        sys.stdin.write(str('var foo="bar"'))
        sys.stdin.seek(0)

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '-ps')

        self.assertEqual(e.exception.args[0], 0)
        self.assertIn(
            'var foo = "bar";\n\n//# sourceMappingURL=', sys.stdout.getvalue())

    def test_pretty_print_stdio_bytes(self):
        self.stub_stdio_bytes()
        sys.stdin.write(b'var foo="bar"')
        sys.stdin.seek(0)

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '-ps')

        self.assertEqual(e.exception.args[0], 0)
        self.assertIn(
            b'var foo = "bar";\n\n//# sourceMappingURL=',
            sys.stdout.getvalue())

    def test_pretty_print_stdio_text(self):
        self.stub_stdio_text()
        sys.stdin.write(u'var foo="bar"')
        sys.stdin.seek(0)

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '-ps')

        self.assertEqual(e.exception.args[0], 0)
        self.assertIn(
            u'var foo = "bar";\n\n//# sourceMappingURL=',
            sys.stdout.getvalue()
        )

    def test_main_all_mangle(self):
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write(dedent("""
            (function(root) {
              var bar = 'bar';

              var foo = function() {
                return bar;
              };

              root.name = 'demo';
              root.foo = foo;
              root.bar = bar;
            })(window)
            """).lstrip())

        self.chdir(root)
        dest = join(root, 'dest.js')
        with self.assertRaises(SystemExit) as e:
            # not actually using '-m' to avoid new flags from future
            # versions
            runtime.main(
                'crimp', 'source.js', '-O', 'dest.js', '-s',
                '--obfuscate', '--drop-semi'
            )

        self.assertEqual(e.exception.args[0], 0)

        with open(dest) as fd:
            self.assertEqual(
                "(function(a){var b='bar';var c=function(){return b};"
                "a.name='demo';a.foo=c;a.bar=b})(window)\n"
                "//# sourceMappingURL=dest.js.map\n",
                fd.read(),
            )

        # implied sourcemap file should be created at the same level at
        # the same dirname.
        # resolve sourcemap name
        dest_map = join(root, 'dest.js.map')
        with open(dest_map) as fd:
            mapping = json.loads(fd.read())
            self.assertEqual(['root', 'bar', 'foo'], mapping['names'])
            self.assertEqual(['source.js'], mapping['sources'])

    def test_source_error(self):
        self.stub_stdio()
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write("function(){};")

        with self.assertRaises(SystemExit) as e:
            # not actually using '-m' to avoid new flags from future
            # versions
            runtime.main('crimp', source)

        self.assertEqual(e.exception.args[0], 1)
        self.assertEqual(
            "Function statement requires a name at 1:9 in %r\n" % source,
            sys.stderr.getvalue())

    def test_unicode_decode_error(self):
        self.stub_stdio()
        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'wb') as fd:
            fd.write(b'var \x82\xcd\x82\xa2 = 1;')

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', source, '--encoding=utf-8')

        self.assertEqual(e.exception.args[0], 1)
        self.assertIn(
            "codec can't decode byte 0x82", sys.stderr.getvalue())

    def test_unicode_encode_error(self):
        self.stub_stdio_bytes()
        sys.stdin.encoding = 'shift_jis'
        sys.stdin.write(b'var \x82\xcd\x82\xa2 = "yes"')
        sys.stdin.seek(0)

        root = self.mkdtemp()
        dest = join(root, 'dest.js')

        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '--encoding=ascii', '-O', dest)

        self.assertEqual(e.exception.args[0], 1)
        self.assertIn(
            "'ascii' codec can't encode characters", sys.stderr.getvalue())

    def test_write_error(self):
        def error():
            raise OSError(28, 'No space left on device')

        self.stub_stdio()
        # cheap way to emulate this, normally this happen with a file...
        sys.stdout.close = error

        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = 1;')

        with self.assertRaises(SystemExit) as e:
            # not actually using '-m' to avoid new flags from future
            # versions
            runtime.main('crimp', source)

        self.assertEqual(e.exception.args[0], 28)
        self.assertIn("No space left on device", sys.stderr.getvalue())

    def test_write_error_fallback(self):
        def error():
            raise IOError()  # not a real valid one, but...

        self.stub_stdio()
        # cheap way to emulate this, normally this happen with a file...
        sys.stdout.close = error

        root = self.mkdtemp()
        source = join(root, 'source.js')
        with open(source, 'w') as fd:
            fd.write('var foo = 1;')

        with self.assertRaises(SystemExit) as e:
            # not actually using '-m' to avoid new flags from future
            # versions
            runtime.main('crimp', source)

        self.assertEqual(e.exception.args[0], 5)

    def test_version_check(self):
        self.stub_stdio()
        with self.assertRaises(SystemExit) as e:
            runtime.main('crimp', '--version')

        self.assertEqual(e.exception.args[0], 0)
        self.assertTrue(sys.stdout.getvalue().startswith('crimp'))

    def test_integration(self):
        p = Popen(['crimp'], stdin=PIPE, stdout=PIPE)
        self.assertEqual(b'var foo=1;', p.communicate(b'var foo = 1;')[0])
