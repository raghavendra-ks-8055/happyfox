"""
Version management for the Email Rules Engine.
This module provides version information and utilities for the application.
"""

import re
from typing import NamedTuple


class Version(NamedTuple):
    """Version information as a named tuple."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return the version as a string."""
        return f"{self.major}.{self.minor}.{self.patch}"


# Current version of the application
# This should be updated when making releases
VERSION = Version(1, 0, 0)

# String representation of the version
__version__ = str(VERSION)


def parse_version(version_str: str) -> Version:
    """Parse a version string into a Version object."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch = map(int, match.groups())
    return Version(major, minor, patch)


def is_compatible(required_version: str) -> bool:
    """Check if the current version is compatible with the required version."""
    required = parse_version(required_version)

    # Major version must match exactly
    if VERSION.major != required.major:
        return False

    # Current minor version must be >= required minor version
    if VERSION.minor < required.minor:
        return False

    # If minor versions match, current patch must be >= required patch
    if VERSION.minor == required.minor and VERSION.patch < required.patch:
        return False

    return True
