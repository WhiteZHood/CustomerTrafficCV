from pathlib import Path

PROJECT_ROOT = Path.cwd()

def project_path(relative_path: str) -> str:
    return PROJECT_ROOT / relative_path
