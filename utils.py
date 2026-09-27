import re

def clean_string(text: str, replace_with: str = "") -> str:
    """
    Removes all spaces, whitespace characters, and special characters from a string,
    leaving only letters, numbers, and underscores.
    """
    # [^\w] or [^a-zA-Z0-9_] matches any character that is NOT alphanumeric or underscore
    return re.sub(r'[^a-zA-Z0-9_]', replace_with, text)

def pull_gdb_from_path(path: str) -> str:
    """
    Extracts the name of the geodatabase (GDB) from a given file path.
    """
    return next((p for p in [path] + list(path.parents) if p.suffix.lower() == ".gdb"), None)