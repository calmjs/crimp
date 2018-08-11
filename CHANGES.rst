Changelog
=========

1.0.1 - 2018-08-11
------------------

- Bumping minimum version of ``calmjs.parse`` to ``1.1.1``, which
  includes fixes to:

  - Line continuation in JavaScript sources should no longer break
    source map line counting.  [
    `calmjs.parse#16 <https://github.com/calmjs/calmjs.parse/issues/16>`_
    ]
  - Will no longer parse certain incorrectly unterminated statements as
    valid JavaScript.  [
    `calmjs.parse#18 <https://github.com/calmjs/calmjs.parse/issues/18>`_
    ]
  - Obfuscated minifier should no longer truncate certain closing braces
    as the internal accounting is corrected.  [
    `calmjs.parse#19 <https://github.com/calmjs/calmjs.parse/issues/19>`_
    ]

1.0.0 - 2017-09-26
------------------

Initial release.
