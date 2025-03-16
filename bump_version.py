#!/usr/bin/env python3
"""
Version bumping script for the Email Rules Engine.

This script helps with bumping the version number in the application.
It updates the version in app/version.py and pyproject.toml.

Usage:
    python bump_version.py [major|minor|patch]
"""
import argparse
import re
import sys
from pathlib import Path

# Define file paths
VERSION_FILE = Path("app/version.py")
PYPROJECT_FILE = Path("pyproject.toml")


def read_current_version():
    """Read the current version from the version file."""
    if not VERSION_FILE.exists():
        print(f"Error: Version file not found at {VERSION_FILE}")
        sys.exit(1)

    content = VERSION_FILE.read_text()
    match = re.search(r"VERSION = Version\((\d+), (\d+), (\d+)\)", content)

    if not match:
        print("Error: Could not find version in version.py")
        sys.exit(1)

    return tuple(map(int, match.groups()))


def bump_version(current_version, bump_type):
    """Bump the version according to the specified type."""
    major, minor, patch = current_version

    if bump_type == "major":
        return (major + 1, 0, 0)
    elif bump_type == "minor":
        return (major, minor + 1, 0)
    elif bump_type == "patch":
        return (major, minor, patch + 1)
    else:
        print(f"Error: Invalid bump type '{bump_type}'")
        sys.exit(1)


def update_version_file(new_version):
    """Update the version in the version.py file."""
    if not VERSION_FILE.exists():
        print(f"Error: Version file not found at {VERSION_FILE}")
        sys.exit(1)

    content = VERSION_FILE.read_text()
    major, minor, patch = new_version

    # Update the version in the file
    new_content = re.sub(
        r"VERSION = Version\(\d+, \d+, \d+\)",
        f"VERSION = Version({major}, {minor}, {patch})",
        content,
    )

    VERSION_FILE.write_text(new_content)
    print(f"Updated {VERSION_FILE} to version {major}.{minor}.{patch}")


def update_pyproject_file(new_version):
    """Update the version in the pyproject.toml file."""
    if not PYPROJECT_FILE.exists():
        print(f"Error: pyproject.toml not found at {PYPROJECT_FILE}")
        sys.exit(1)

    content = PYPROJECT_FILE.read_text()
    version_str = ".".join(map(str, new_version))

    # Update the version in the file
    new_content = re.sub(
        r'version = "(\d+\.\d+\.\d+)"', f'version = "{version_str}"', content
    )

    PYPROJECT_FILE.write_text(new_content)
    print(f"Updated {PYPROJECT_FILE} to version {version_str}")


def main():
    """Main function to handle version bumping."""
    parser = argparse.ArgumentParser(
        description="Bump the version of the Email Rules Engine"
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="The type of version bump to perform",
    )

    args = parser.parse_args()

    # Read the current version
    current_version = read_current_version()
    current_version_str = ".".join(map(str, current_version))
    print(f"Current version: {current_version_str}")

    # Bump the version
    new_version = bump_version(current_version, args.bump_type)
    new_version_str = ".".join(map(str, new_version))
    print(f"New version: {new_version_str}")

    # Update the files
    update_version_file(new_version)
    update_pyproject_file(new_version)

    print(
        f"Successfully bumped version from {current_version_str} to {new_version_str}"
    )


if __name__ == "__main__":
    main()
