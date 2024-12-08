"""
The entrypoint for the application.
"""

import argparse
import functools
import json
import logging
import os
import shutil
import sys
from concurrent.futures import (
    ProcessPoolExecutor,
    as_completed,
    BrokenExecutor,
)
from argparse import Namespace
from datetime import datetime
from typing import Iterator, List, Iterable, Callable

from bgs_tool import BYTES_IN_MB
from bgs_tool.helpers.helpers_benchmark import benchmark
from bgs_tool.helpers.helpers_files import create_temp_dir_with_test_files
from bgs_tool.helpers.helpers_logging import (
    get_logger,
    get_default_log_filepath,
)
from bgs_tool.types import FileAttributes

DEFAULT_MAX_FILES = 15
DEFAULT_MIN_FILES = 5
DEFAULT_MAX_FILES_BYTES = 15 * BYTES_IN_MB
DEFAULT_MIN_FILES_BYTES = 5 * BYTES_IN_MB


def _validate_path(path: str):
    """
    Validate the path parameter.
    :param path:
    :return:
    """
    if not isinstance(path, str):
        raise argparse.ArgumentTypeError(
            "The directory specified is not a string."
        )
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            f"The directory does not exist: {path}"
        )

    return path


def parse_arguments() -> Namespace:
    """
    Parse command-line arguments using argparse.

    :returns: Parsed arguments.
    :rtype: Namespace
    """

    def positive_int(value: str) -> int:
        """
        Validate the value specified
        :param value:
        :return:
        """
        if value is None:
            raise ValueError("Value cannot be None")
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"'{value}' must be a positive integer."
            )
        return ivalue

    def validate_test_file_args(parsed_args: Namespace):
        """
        Validate the arguments used for test files.
        :param parsed_args:
        :return:
        """
        if not parsed_args or parsed_args is None:
            raise ValueError("The arguments are invalid or null")

        if parsed_args.create_test_files:
            for param in [
                "max_files",
                "min_files",
                "max_file_size_bytes",
                "min_file_size_bytes",
            ]:
                if (
                    param in parsed_args
                    and getattr(parsed_args, param, None) is None
                ):
                    raise argparse.ArgumentTypeError(
                        f"'{param}' cannot be None when "
                        f'"--create-test-files" is defined.'
                    )

            if all(
                [
                    getattr(parsed_args, "max_files", None) is not None,
                    getattr(parsed_args, "min_files", None) is not None,
                ]
            ) and not all(
                [
                    parsed_args.min_files <= parsed_args.max_files,
                    parsed_args.min_file_size_bytes
                    <= parsed_args.max_file_size_bytes,
                ]
            ):
                raise argparse.ArgumentTypeError(
                    "Ensure 'min_files <= max_files' and "
                    "'min_file_size_bytes <= max_file_size_bytes' "
                    "when creating test files."
                )

    parser = argparse.ArgumentParser(
        prog="bgs-tool",
        description="Group files in a directory based on size "
        "limits and save group details in JSON files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Define mutually exclusive group for source-dir and create-test-files
    source_files_group = parser.add_mutually_exclusive_group(required=True)
    source_files_group.add_argument(
        "--source-dir",
        type=_validate_path,
        default=os.getcwd(),
        help="Path to the source directory to scan for files.",
    )
    source_files_group.add_argument(
        "--create-test-files",
        action="store_true",
        help="Generate test files for testing purposes.",
    )

    # Parameters for test file generation
    parser.add_argument(
        "--max-files",
        type=positive_int,
        default=DEFAULT_MAX_FILES,
        help="Max files for test generation.",
    )
    parser.add_argument(
        "--min-files",
        type=positive_int,
        default=DEFAULT_MIN_FILES,
        help="Min files for test generation.",
    )
    parser.add_argument(
        "--max-file-size-bytes",
        type=positive_int,
        default=DEFAULT_MAX_FILES_BYTES,
        help="Max file size in bytes for test generation.",
    )
    parser.add_argument(
        "--min-file-size-bytes",
        type=positive_int,
        default=DEFAULT_MIN_FILES_BYTES,
        help="Min file size in bytes for test generation.",
    )

    # Group size arguments (mutually exclusive)
    file_group_sizes = parser.add_mutually_exclusive_group(required=True)
    file_group_sizes.add_argument(
        "--max-group-size-megabytes",
        type=positive_int,
        help="Max group size in MB.",
    )
    file_group_sizes.add_argument(
        "--max-group-size-bytes",
        type=positive_int,
        help="Max group size in bytes.",
    )

    # Additional general arguments
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(os.getcwd(), "groups"),
        help="Output directory to save group files.",
    )
    parser.add_argument(
        "--log-filepath",
        type=str,
        default=get_default_log_filepath(),
        help="Absolute path for the log file.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Silence logging output."
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate groups after processing to check size limits.",
    )
    parser.add_argument(
        "--method",
        choices=["compact", "default"],
        default="compact",
        help="Method for grouping files.",
    )

    args = parser.parse_args(sys.argv[1:])

    validate_test_file_args(args)

    if not args.create_test_files and not os.path.isdir(args.source_dir):
        raise FileNotFoundError(
            f"Source directory '{args.source_dir}' does not exist."
        )
    return args


def list_files(
    source_dir: str, logger: logging.Logger
) -> Iterator[os.DirEntry]:
    """
    Lazily list files in the source directory
    (non-recursively) using os.scandir.

    :param source_dir: Path to the source directory.
    :type source_dir: str
    :param logger: Logger instance for logging.
    :type logger: logging.Logger

    :yields: DirEntry objects for files in the source directory.
    :rtype: Iterator[os.DirEntry]
    """
    if not source_dir:
        raise ValueError("'source_dir' must not be empty.")
    if not os.path.isdir(source_dir):
        raise IOError(f"Source directory '{source_dir}' does not exist.")
    if not logger:
        raise ValueError("The logger instance is invalid or null.")

    try:
        """
        Use "os.scandir" to iterate over files in the source
        directory instead of "os.listdir".

        Using "os.listdir" would cause for two separate iterations:

            1. Iterating over files in the directory, and
              populating a list ("os.listdir")
            2. Iterating over the populated list in the
              calling function ("get_file_attributes", etc.).

        This is not ideal ^

        The source directory could have a lot of files in it,
        which could potentially take a long time to populate
        and would increase memory consumption of the application.

        Instead, use "os.scandir" which dynamically traverses
        the files in the path, and use "yield" to implicitly return
        an "Iterable" or generator that evaluates to individual items
        in the source directory that are files.
        """
        with os.scandir(source_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    yield entry
    except IOError as e:
        logger.exception(
            f"Error listing files in directory '{source_dir}': {e}", exc_info=e
        )
        sys.exit(-1)


def _get_file_attribute(file_path: str) -> FileAttributes:
    """

    :param file_path: The absolute path tothe file.
    :return:
    """
    if not file_path:
        raise ValueError("The file entry specified is invalid or null.")
    stat_result = os.stat(file_path)
    return {
        "name": os.path.basename(file_path),
        "size_bytes": stat_result.st_size,
        "last_modified": datetime.fromtimestamp(
            stat_result.st_mtime
        ).isoformat(),
    }


@benchmark
def get_file_attributes(
    source_dir: str, logger: logging.Logger
) -> Iterator[FileAttributes]:
    """
    Yield file attributes from the specified source directory.

    This function is separate to "list_files" so that
    they can be mocked individually for unit testing purposes.

    For example, the patched version of "list_files" can be
    mocked to have a .return_value of an arbitrary
    list of test data, which can then
    be sourced by dependent functions like "get_file_attributes".

    :param source_dir: Path to the source directory.
    :type source_dir: str
    :param logger: Logger instance for logging.
    :type logger: logging.Logger

    :yields: File attributes as a dictionary.
    :rtype: Iterator[FileAttributes]
    """
    if not source_dir:
        raise ValueError("'source_dir' must not be empty.")
    if not logger:
        raise ValueError("The logger instance is invalid or null.")

    try:
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(_get_file_attribute, task.path): task
                for task in list_files(source_dir, logger)
            }

            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    yield result
                except FileNotFoundError as exc:
                    logger.exception(
                        f"Error retrieving information for file '{exc.filename}': {exc}",
                        exc_info=exc,
                    )
                except IOError as exc:
                    logger.exception(
                        f"Error listing files in directory '{source_dir}': {exc}",
                        exc_info=exc,
                    )
    except BrokenExecutor as exc:
        logger.exception(f"Broken executor: {exc}", exc_info=exc)


@benchmark
def group_files(
    files: Iterable[FileAttributes],
    max_group_size_bytes: int,
    logger: logging.Logger,
) -> List[List[FileAttributes]]:
    """
    Groups files into sublist based on size constraints.

    :param logger: Logger instance for logging warnings
    :param files: The files to process into groups
    :param max_group_size_bytes: The max amount of bytes per group
    :return: List of grouped files
    """
    if not files:
        raise ValueError("'files' must not be empty.")
    if not max_group_size_bytes:
        raise ValueError("'max_group_size_bytes' must not be empty.")
    if not logger:
        raise ValueError("The logger instance is invalid or null.")

    groups: List[List[FileAttributes]] = []
    current_group: List[FileAttributes] = []
    current_group_size_remaining = max_group_size_bytes

    for file in files:
        current_file_name: str = file["name"]
        current_file_size_bytes: int = file["size_bytes"]
        logger.debug(
            f"Processing file: '{current_file_name}' "
            f"({current_file_size_bytes} bytes)"
        )

        if current_file_size_bytes > max_group_size_bytes:
            logger.warning(
                f"File '{current_file_name}' exceeds the maximum group "
                f"size and will be skipped."
            )
            continue

        if current_file_size_bytes <= current_group_size_remaining:
            current_group_size_remaining -= current_file_size_bytes
            current_group.append(file)
        else:
            groups.append(current_group)
            current_group = [file]
            current_group_size_remaining = (
                max_group_size_bytes - current_file_size_bytes
            )

    if current_group:  # Add the last group if it contains files
        groups.append(current_group)

    return groups


@benchmark
def group_files_compact(
    files: Iterable[FileAttributes],
    max_group_size_bytes: int,
    logger: logging.Logger,
) -> List[List[FileAttributes]]:
    """
    Group files as compactly as possible. Files will be inserted into
    existing groups using the smallest (but large enough) available spaces.

    :param files: List of file attributes.
    :type files: List[FileAttributes]
    :param max_group_size_bytes: Maximum size of each group in bytes.
    :type max_group_size_bytes: int
    :param logger: Logger instance for logging.
    :type logger: logging.Logger

    :returns: A list of groups, where each group is a list of file attributes.
    :rtype: List[List[FileAttributes]]
    """
    if not files:
        raise ValueError("'files' must not be empty.")
    if not max_group_size_bytes:
        raise ValueError("'max_group_size_bytes' must not be empty.")
    if not logger:
        raise ValueError("The logger instance is invalid or null.")

    groups: List[List[FileAttributes]] = []
    group_sizes: List[int] = []
    for file in files:
        current_file_name: str = file["name"]
        current_file_size_bytes: int = file["size_bytes"]
        logger.debug(
            f"Processing file: '{current_file_name}' "
            f"({current_file_size_bytes} bytes)"
        )

        if current_file_size_bytes > max_group_size_bytes:
            logger.warning(
                f"File '{current_file_name}' exceeds the maximum group "
                f"size and will be skipped."
            )
            continue

        tightest_fitting_group_index = -1
        tightest_fitting_group_size_bytes = max_group_size_bytes + 1

        """
        Iterate over the groups, if any exist, and find one
        that fits best.
        
        If none fit best, or if there are not any (first iteration),
        then create a new group.
        
        The group with the smallest, but large enough,
        available space takes precedence.
        
        This secondary loop could likely be optimized for insert/retrieval.
        """
        for current_group_index, current_group_size_bytes in enumerate(
            group_sizes
        ):
            remaining_current_group_size_bytes = (
                max_group_size_bytes - current_group_size_bytes
            )
            if (
                current_file_size_bytes <= remaining_current_group_size_bytes
                and remaining_current_group_size_bytes
                - current_file_size_bytes
                < tightest_fitting_group_size_bytes
            ):
                tightest_fitting_group_index = current_group_index
                tightest_fitting_group_size_bytes = (
                    remaining_current_group_size_bytes
                    - current_file_size_bytes
                )

        # If none fit best, or if there are not any (first iteration), then create a new group.
        if tightest_fitting_group_index != -1:
            groups[tightest_fitting_group_index].append(file)
            group_sizes[
                tightest_fitting_group_index
            ] += current_file_size_bytes
            if (
                group_sizes[tightest_fitting_group_index]
                == max_group_size_bytes
            ):
                group_sizes.pop(tightest_fitting_group_index)
        else:
            # None found, or first iteration.
            groups.append([file])
            group_sizes.append(current_file_size_bytes)

    return groups


@benchmark
def save_groups(
    groups: List[List[FileAttributes]], output_dir: str, logger: logging.Logger
) -> None:
    """
    Save each group to a JSON file in the output directory.

    :param groups: List of groups to save.
    :type groups: List[List[FileAttributes]]
    :param output_dir: Path to the output directory.
    :type output_dir: str
    :param logger: Logger instance for logging.
    :type logger: logging.Logger
    """
    if not groups:
        raise ValueError("No groups to save.")
    if not logger:
        raise ValueError("The logger instance is invalid or null.")
    if not output_dir:
        raise ValueError("The output directory is invalid or null.")

    try:
        if os.path.isdir(output_dir):
            logger.warning("Deleting existing output directory.")
            shutil.rmtree(output_dir)
        logger.warning("Creating output directory %s", output_dir)
        os.makedirs(output_dir, exist_ok=True)
    except IOError as filesystem_error:
        logger.exception(
            f"Error creating output directory "
            f"'{output_dir}': {filesystem_error}",
            exc_info=filesystem_error,
        )
        sys.exit(-1)

    """
    This "save" operation could paralleled across several processes 
    using "multiprocessing" and "ProcessPoolExecutor" with a 
    defined upper limit of workers ("num_workers").
    
    This is ideal in scenarios where there are a lot of groups to save, but
    might be a premature optimization for an application of this scope.
    """
    for index, group in enumerate(groups):
        group_file_path: str = os.path.join(
            output_dir, f"group_{index + 1:03d}.json"
        )
        try:
            logger.info(f'Saving: "{group_file_path}"')
            with open(group_file_path, "w", encoding="utf-8") as file:
                json.dump(group, file, indent=4)
        except FileExistsError as file_exists_error:
            logger.exception(
                f"Error writing group file '{group_file_path}'"
                f": {file_exists_error}",
                exc_info=file_exists_error,
            )
            sys.exit(-1)


def validate_groups(
    groups: List[List[FileAttributes]],
    max_group_size_bytes: int,
    logger: logging.Logger,
) -> None:
    """
    Validate the groups that were generated or produced.
    :param logger: The logger instance.
    :param groups: The groups.
    :param max_group_size_bytes: The max size of each group in bytes.
    :return:
    """
    valid_groups = []
    for group in groups:
        if (
            functools.reduce(lambda a, b: a + b["size_bytes"], group, 0)
            <= max_group_size_bytes
        ):
            valid_groups.append(group)

    logger.info("%d valid groups out of %d", len(valid_groups), len(groups))


def main() -> None:
    """
    Main function to execute the script logic.

    :returns: None
    """
    args: Namespace = parse_arguments()
    if not args:
        raise ValueError("No arguments provided.")
    logger: logging.Logger = get_logger(filepath=args.log_filepath)
    if not logger:
        raise ValueError("Logger instance is invalid or null.")

    if args.quiet:
        logging.disable(logging.CRITICAL)

    if not args.method:
        raise ValueError("The method was not defined (--method)")

    source_dir: str | None = args.source_dir

    # This has been used for testing purposes and generating files of various sizes.
    if args.create_test_files or source_dir is None:
        logger.debug(f"Max Files: %s", args.max_files)
        logger.debug(f"Min Files: %s", args.min_files)
        logger.debug(f"Max File Size Bytes: %s", args.max_file_size_bytes)
        logger.debug(f"Min File Size Bytes: %s", args.min_file_size_bytes)
        with create_temp_dir_with_test_files(
            max_files=args.max_files,
            min_files=args.min_files,
            max_file_size_bytes=args.max_file_size_bytes,
            min_file_size_bytes=args.min_file_size_bytes,
        ) as temp_dir:
            source_dir = temp_dir

    max_group_size_bytes: int = (
        args.max_group_size_megabytes * BYTES_IN_MB
        if args.max_group_size_megabytes is not None
        else args.max_group_size_bytes
    )

    logger.info(f"Group Files: {args.method}")
    callable_group_files: dict[
        str,
        Callable[
            [Iterable[FileAttributes], int, logging.Logger],
            List[List[FileAttributes]],
        ],
    ] = {
        "compact": group_files_compact,
        "default": group_files,
    }
    if args.method not in callable_group_files:
        raise KeyError(f"Unable to find grouping method '{args.method}'.")

    grouping_function = {
        "compact": group_files_compact,
        "default": group_files,
    }[args.method]
    groups = grouping_function(
        get_file_attributes(source_dir, logger), max_group_size_bytes, logger
    )

    if not groups:
        logger.warning("No groups to save.")
    else:
        logger.info(
            f"Grouped {sum(len(g) for g in groups)} files into {len(groups)} groups."
        )

    save_groups(groups, args.output_dir, logger)
    if args.validate:
        validate_groups(groups, max_group_size_bytes, logger)

    logger.info(
        "Successfully grouped files into %s group(s) and saved to '%s'.",
        len(groups),
        args.output_dir,
    )


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(-1)
