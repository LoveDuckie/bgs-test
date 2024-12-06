"""
    Helper classes or types for producing groups of files.
"""

from dataclasses import dataclass
import functools
from typing import Iterator, TypedDict


class FileAttributes(TypedDict):
    """
    A typed dictionary representing file attributes.

    :param name: The name of the file.
    :type name: str
    :param size_bytes: The size of the file in bytes.
    :type size_bytes: int
    :param last_modified: The last modified date of
    the file in ISO 8601 format.
    :type last_modified: str
    """

    name: str
    size_bytes: int
    last_modified: str


@dataclass
class FileInformation:
    """
    Same as FileAttributes, but for file information
    described as a dataclass.
    """

    name: str
    size_bytes: int
    last_modified: str


class FileGroup:
    """
    A group of files that belong to this group.
    """

    def __init__(self, files: list[FileAttributes] = None):
        """

        :param files:
        """
        self._files = files if files is not None else []
        self._total_size_bytes = (
            0
            if files is None
            else functools.reduce(lambda a, b: a + b.size_bytes, files, 0)
        )

    def append(self, file: FileAttributes):
        """

        :param file:
        :return:
        """
        if file is None:
            raise ValueError("File cannot be None")

        self._files.append(file)
        self._total_size_bytes = self.total_size_bytes + file["size_bytes"]

    @property
    def files(self):
        """

        :return:
        """
        return self._files

    @property
    def total_size_bytes(self):
        """

        :return:
        """
        return self._total_size_bytes

    def __iter__(self) -> Iterator[FileAttributes]:
        """

        :return:
        """
        for f in self._files:
            yield f

    def __len__(self) -> int:
        """

        :return:
        """
        return len(self._files)
