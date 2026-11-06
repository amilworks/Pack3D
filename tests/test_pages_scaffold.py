import importlib.util
from pathlib import Path
import pytest


def test_pages_rejects_root_traversal_and_linked_content(tmp_path):
    source = Path(__file__).resolve().parents[1] / "tools/check_pages_artifact.py"
    spec = importlib.util.spec_from_file_location("pages_check", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for value in (".", "..", "/tmp", "missing"):
        with pytest.raises(ValueError):
            module.validate(tmp_path, value)
    site = tmp_path / "website"
    site.mkdir()
    (site / "index.html").write_text("<h1>Author site</h1>")
    assert module.validate(tmp_path, "website") == site
    (site / "linked").symlink_to(source)
    with pytest.raises(ValueError, match="linked"):
        module.validate(tmp_path, "website")


def test_repository_website_is_deployable():
    root = Path(__file__).resolve().parents[1]
    if not (root / "website").is_dir():
        pytest.skip("website/ is not part of the source distribution")
    source = root / "tools/check_pages_artifact.py"
    spec = importlib.util.spec_from_file_location("pages_check", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.validate(root, "website") == root / "website"
