"""
File operation tools for the FileOperationsAgent.

These tools provide file system operations like reading, writing,
listing, and deleting files.
"""

import os
from pathlib import Path
from typing import List
from langchain.tools import tool


@tool
def read_file(filepath: str) -> str:
    """
    Read the contents of a file.

    This tool reads and returns the complete contents of a file.
    Useful for reading configuration files, documents, or any text-based files.

    Args:
        filepath: Path to the file to read (can be relative or absolute)

    Returns:
        str: The contents of the file

    Example:
        read_file("data/notes.txt")
    """
    try:
        path = Path(filepath).expanduser()

        if not path.exists():
            return f"Error: File '{filepath}' does not exist."

        if not path.is_file():
            return f"Error: '{filepath}' is not a file."

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"Successfully read file '{filepath}':\n\n{content}"

    except PermissionError:
        return f"Error: Permission denied to read '{filepath}'."
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


@tool
def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file.

    This tool writes the provided content to a file. If the file exists,
    it will be overwritten. Parent directories are created if they don't exist.

    Args:
        filepath: Path to the file to write (can be relative or absolute)
        content: The content to write to the file

    Returns:
        str: Success or error message

    Example:
        write_file("output/result.txt", "Hello, World!")
    """
    try:
        path = Path(filepath).expanduser()

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to '{filepath}'."

    except PermissionError:
        return f"Error: Permission denied to write to '{filepath}'."
    except Exception as e:
        return f"Error writing to file '{filepath}': {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """
    List all files and directories in a given directory.

    This tool provides a listing of all items in a directory,
    distinguishing between files and subdirectories.

    Args:
        directory: Path to the directory to list (defaults to current directory)

    Returns:
        str: Formatted list of files and directories

    Example:
        list_files("data/")
    """
    try:
        path = Path(directory).expanduser()

        if not path.exists():
            return f"Error: Directory '{directory}' does not exist."

        if not path.is_dir():
            return f"Error: '{directory}' is not a directory."

        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        if not items:
            return f"Directory '{directory}' is empty."

        result = [f"Contents of '{directory}':\n"]

        dirs = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]

        if dirs:
            result.append("Directories:")
            for item in dirs:
                result.append(f"  📁 {item.name}/")

        if files:
            result.append("\nFiles:")
            for item in files:
                size = item.stat().st_size
                result.append(f"  📄 {item.name} ({size} bytes)")

        return "\n".join(result)

    except PermissionError:
        return f"Error: Permission denied to access '{directory}'."
    except Exception as e:
        return f"Error listing directory '{directory}': {str(e)}"


@tool
def delete_file(filepath: str) -> str:
    """
    Delete a file.

    This tool permanently deletes a file from the file system.
    Use with caution as this operation cannot be undone.

    Args:
        filepath: Path to the file to delete

    Returns:
        str: Success or error message

    Example:
        delete_file("temp/old_file.txt")
    """
    try:
        path = Path(filepath).expanduser()

        if not path.exists():
            return f"Error: File '{filepath}' does not exist."

        if not path.is_file():
            return f"Error: '{filepath}' is not a file. Use a different tool to delete directories."

        path.unlink()
        return f"Successfully deleted file '{filepath}'."

    except PermissionError:
        return f"Error: Permission denied to delete '{filepath}'."
    except Exception as e:
        return f"Error deleting file '{filepath}': {str(e)}"


@tool
def append_to_file(filepath: str, content: str) -> str:
    """
    Append content to an existing file.

    This tool adds content to the end of a file without overwriting
    existing content. Creates the file if it doesn't exist.

    Args:
        filepath: Path to the file to append to
        content: The content to append

    Returns:
        str: Success or error message

    Example:
        append_to_file("log.txt", "New log entry\\n")
    """
    try:
        path = Path(filepath).expanduser()

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully appended {len(content)} characters to '{filepath}'."

    except PermissionError:
        return f"Error: Permission denied to write to '{filepath}'."
    except Exception as e:
        return f"Error appending to file '{filepath}': {str(e)}"
