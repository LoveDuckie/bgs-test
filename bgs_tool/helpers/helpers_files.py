"""
Helpers: Files
"""

import os
import tempfile
import random

from bgs_tool import BYTES_IN_MB


def create_temp_dir_with_test_files(
    *,
    min_files: int | None = 1,
    max_files: int | None = 100,
    min_file_size_bytes: int = 1 * BYTES_IN_MB,
    max_file_size_bytes: int = 5 * BYTES_IN_MB,
) -> tempfile.TemporaryDirectory:
    """
    Create a temporary directory to use for testing purposes.
    :param min_file_size_bytes: The minimum size of files to create.
    :param max_file_size_bytes: The maximum size of files to create.
    :param min_files: The maximum number of files to create.
    :param max_files: The minimum number of files to create.
    :return:
    """
    temp_dir = tempfile.TemporaryDirectory(delete=False)
    create_test_files(
        path=temp_dir.name,
        min_files=min_files,
        max_files=max_files,
        min_file_size_bytes=min_file_size_bytes,
        max_file_size_bytes=max_file_size_bytes,
    )
    return temp_dir


def create_test_files(
    *,
    path: str | None = None,
    min_files: int | None = 1,
    max_files: int | None = 100,
    min_file_size_bytes: int = 1 * BYTES_IN_MB,
    max_file_size_bytes: int = 5 * BYTES_IN_MB,
):
    """
    Create a temporary directory and return its path.
    temporary directory will be created.
    :return: Returns the instantiated temporary directory.
    """
    num_files: int = random.randint(min_files, max_files)
    if path is not None:
        if not os.path.isdir(path):
            raise IOError(f"The path {path} could not be found")
    temp_output_path: str = tempfile.mkdtemp() if path is None else path
    pattern = b"ABC"

    for i in range(num_files):
        file_path = os.path.join(temp_output_path, "file{:03d}.txt".format(i))
        # Open the file for write in binary mode.
        with open(file_path, "wb") as f:
            remaining_file_size_bytes: int = random.randint(
                min_file_size_bytes, max_file_size_bytes
            )
            chunk_size = BYTES_IN_MB
            data = pattern * (chunk_size // len(pattern))

            while remaining_file_size_bytes > 0:
                to_write = min(chunk_size, remaining_file_size_bytes)
                f.write(data[:to_write])
                remaining_file_size_bytes -= to_write
