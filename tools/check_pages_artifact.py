"""Reject accidental source-tree deployment; only an explicit static site is valid."""
import argparse
from pathlib import Path


def validate(root, value):
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("site_path must be a relative directory without '..'")
    target = (root / relative).resolve()
    if target == root or not target.is_relative_to(root):
        raise ValueError("do not deploy the repository root or a directory outside it")
    if (root / relative).is_symlink() or not (target / "index.html").is_file():
        raise ValueError("site directory must contain index.html and cannot be a symlink")
    for item in target.rglob("*"):
        if item.is_symlink() or (item.is_file() and item.stat().st_nlink > 1):
            raise ValueError(f"linked files cannot be deployed: {item.name}")
        if item.name == ".git" or item.name.startswith(".env") or item.suffix in (".pem", ".key", ".pt", ".ckpt"):
            raise ValueError(f"private/source artifact in site output: {item.name}")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_path")
    args = parser.parse_args()
    print(validate(Path.cwd().resolve(), args.site_path))
