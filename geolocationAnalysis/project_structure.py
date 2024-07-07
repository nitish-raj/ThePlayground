import os


def print_directory_structure(startpath, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, "").count(os.sep)
        indent = "    " * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = "    " * (level + 1)
        for f in files:
            if f not in exclude_files:
                print(f"{subindent}{f}")


# Usage
if __name__ == "__main__":
    project_path = "."  # Current directory
    exclude_dirs = {".git", "__pycache__", "venv", "google-cloud-sdk"}
    exclude_files = {".gitignore", ".DS_Store"}  # Common files to exclude
    print_directory_structure(project_path, exclude_dirs, exclude_files)
