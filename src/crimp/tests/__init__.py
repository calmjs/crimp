# -*- coding: utf-8 -*-
import unittest


def make_suite():  # pragma: no cover
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('crimp.tests', pattern='test_*.py')
    return test_suite
