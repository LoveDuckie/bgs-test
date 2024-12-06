"""
Tests: Parse Arguments
"""

import unittest
from argparse import Namespace
from typing import Iterable
from unittest.mock import MagicMock, patch

from bgs_tool import BYTES_IN_MB
from bgs_tool.__main__ import group_files_compact, parse_arguments
from bgs_tool.types import FileAttributes


class TestParseArguments(unittest.TestCase):
    """
    Unit tests for the `parse_arguments` function.
    """

    @patch("argparse.ArgumentParser.parse_args")
    @patch("os.path.isdir", return_value=True)
    def test_parse_arguments_valid(self, mock_isdir, mock_parse_args):
        """
        Test `parse_arguments` with valid arguments.

        :param mock_isdir: Mock for `os.path.isdir` to
        simulate a valid directory.
        :param mock_parse_args: Mock for `argparse.ArgumentParser.parse_args`
        to provide test input.
        :assert: Parsed arguments match the expected values.
        """
        if not mock_isdir:
            raise ValueError(
                "The mocked version of os.path.isdir is invalid or null"
            )
        mock_parse_args.return_value = Namespace(
            source_dir="source",
            max_files=None,
            min_files=None,
            min_file_size_bytes=None,
            max_file_size_bytes=None,
            create_test_files=None,
            max_group_size_bytes=None,
            max_group_size_megabytes=10,
            output_dir="output",
        )
        args = parse_arguments()
        self.assertIsInstance(args, Namespace)
        self.assertEqual(args.source_dir, "source")
        self.assertEqual(args.max_group_size_megabytes, 10)

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_arguments_invalid_group_size(self, mock_parse_args):
        """
        Test `parse_arguments` with an invalid group size.

        :param mock_parse_args: Mock for
        `argparse.ArgumentParser.parse_args` to provide invalid input.
        :assert: ValueError is raised for invalid `max_group_size_megabytes`.
        """
        mock_parse_args.return_value = Namespace(
            source_dir="source",
            max_group_size_megabytes=-1,
            output_dir="output",
            max_files=None,
            min_files=None,
            min_file_size_bytes=None,
            max_file_size_bytes=None,
            create_test_files=None,
            max_group_size_bytes=None,
        )
        with self.assertRaises(FileNotFoundError):
            with self.assertRaises(ValueError):
                parse_arguments()

    def test_group_files_skip_large_files(self):
        """
        Test `group_files` with a file larger than the group size.

        :assert: Large files are skipped and not included in any group.
        """
        files: Iterable[FileAttributes] = [
            {
                "name": "file1",
                "size_bytes": int(1.5 * BYTES_IN_MB),
                "last_modified": "2024-12-03T12:00:00",
            }
        ]
        logger = MagicMock()
        groups = group_files_compact(files, 1000, logger)
        self.assertEqual(len(groups), 0)
