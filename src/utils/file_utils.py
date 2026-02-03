
import json
import os
from pathlib import Path
from typing import Any, List


def check_folder_and_create(folder: str) -> None:
    """
    TS: if (!fs.existsSync(folder)) fs.mkdirSync(folder, { recursive: true });
    Python: mkdir(parents=True, exist_ok=True)
    """
    Path(folder).mkdir(parents=True, exist_ok=True)


def write_json_data(file_path: str, data: Any) -> None:
    """
    TS: fs.writeFileSync(filePath, JSON.stringify(data, null, 2), { flag: 'w' }, 'utf-8');
    Python: json.dump(..., indent=2) with utf-8 encoding (overwrite)
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)  # optional convenience
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json_data(file_path: str) -> Any:
    """
    TS: JSON.parse(fs.readFileSync(filePath))
    Python: json.load()
    """
    with Path(file_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_data(file_path: str) -> bytes:
    """
    TS: const data = fs.readFileSync(filePath); return data;
    Python: read bytes
    """
    return Path(file_path).read_bytes()


def is_file_exist(file_path: str) -> bool:
    """
    TS: fs.existsSync(filepath)
    Python: Path.exists()
    """
    return Path(file_path).exists()


def get_file_names_from_dir(dir_path: str) -> List[str]:
    """
    TS: fs.readdirSync(dirPath) -> file names
    Python: listdir or Path.iterdir (names only)
    """
    p = Path(dir_path)
    return [x.name for x in p.iterdir() if x.exists()]


def get_full_file_names(dir_path: str, file_name_substring: str) -> List[str]:
    """
    TS: returns filenames that include substring
    Python: filter by substring in name
    """
    p = Path(dir_path)
    return [x.name for x in p.iterdir() if x.exists() and file_name_substring in x.name]


def make_empty_folder(dir_path: str) -> None:
    """
    TS (fs-extra):
      ensureDir(dirPath);
      emptyDir(dirPath);

    Python:
      - ensure directory exists
      - delete all contents inside it (files + subfolders)
    """
    p = Path(dir_path)
    p.mkdir(parents=True, exist_ok=True)

    # Remove all contents inside the directory
    for child in p.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            # recursively remove directory
            _remove_tree(child)


def _remove_tree(path: Path) -> None:
    """Recursive directory delete (like shutil.rmtree but minimal)."""
    for child in path.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        else:
            _remove_tree(child)
    path.rmdir()
 
