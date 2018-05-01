"""Some basic tests for dprint.

Because of course I wrote tests for it. :)
"""

import sys
import os

import pytest

import dprint._impl as impl


class TestLineNumberFormatting(object):

    def test_given_None(self):
        assert impl._format_lineno(None) == ""

    @pytest.mark.parametrize("given, expected", [
        (0, ":0"),
        (1, ":1"),
        (1024, ":1024"),
    ])
    def test_given_an_integer(self, given, expected):
        assert impl._format_lineno(given) == expected


class TestFileNameFormatting(object):

    def test_given_None(self):
        assert impl._format_filename(None) == "<unknown-file>"

    @pytest.mark.parametrize("given, expected", [
        ("my_script.py", "my_script.py"),
        ("./my_script.py", "my_script.py"),
        ("folder/my_script.py", "folder/my_script.py"),
        ("./folder/my_script.py", "folder/my_script.py"),
    ])
    def test_given_a_filename_in_current_working_dir(self, given, expected):
        assert impl._format_filename(given) == expected

    @pytest.mark.parametrize("given, expected", [
        ("pkg.py", "<installed> pkg"),
        ("pkg/submodule.py", "<installed> pkg.submodule"),
    ])
    def test_given_a_filename_in_sys_path(self, given, expected):
        sys.path.append("/my/awesome/python/lib/site-packages")
        path = os.path.join(os.path.normcase(sys.path[-1]), given)
        assert impl._format_filename(path) == expected
        sys.path.pop(-1)

    @pytest.mark.parametrize("path", [
        "/awesome/weird/place/file.py",
        "/awesome/weird/place/pkg/__init__.py",
    ])
    def test_given_an_filename_in_different_place(self, path):
        assert impl._format_filename(path) == path


class TestFunctionNameFormatting(object):

    def test_given_None(self):
        assert impl._format_function(None) == ""

    @pytest.mark.parametrize("given, expected", [
        ("<module>", " (top level stmt)"),
        ("function", " in function"),
        ("main", " in main"),
    ])
    def test_given_a_name(self, given, expected):
        assert impl._format_function(given) == expected


class TestValueFormatting(object):

    def test_given_non_repr_convertable(self):

        class NonStringConverting(object):
            def __repr__(self):
                raise Exception("No.")

        assert (
            impl._format_value(NonStringConverting()) ==
            "<could not convert to string>"
        )

    @pytest.mark.parametrize("given, expected", [
        ("string", "'string'"),
        (1, "1"),
        (1.2, "1.2"),
    ])
    def test_given_a_name(self, given, expected):
        assert impl._format_value(given) == expected



class TestExpressionExtraction(object):

    def test_given_None(self):
        assert impl._format_expression(None) == ""

    @pytest.mark.parametrize("given, expected", [
        ("dprint(x)", "x"),
        ("dprint(x + y)", "x + y"),
        ("    dprint(x + y)", "x + y"),
        ("dprint((x - 6) * y)", "(x - 6) * y"),
        ("dprint(f(x, y=z))", "f(x, y=z)"),
        ("dprint(dprint(x))", "dprint(x)"),  # to make sure it doesn't crash.
    ])
    def test_given_a_line_of_code(self, given, expected):
        assert impl._format_expression([given]) == expected
