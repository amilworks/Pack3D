"""Release-hygiene checks for the repository. Run from anywhere: ``python tools/check_release.py``.

Checks local Markdown links and their #anchors, YAML syntax, Python syntax, pinned GitHub Actions,
the website workflow's permissions and the folder it deploys, the versions the page asks its scripts by,
the checksums of the frozen results and paper recipes, and that the version agrees across the package,
CITATION.cff and CHANGELOG.md.
It also looks for a few common secret patterns. It is not a substitute for a full secret scanner.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_pages_artifact import validate as validate_site  # noqa: E402

EXCLUDED = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist", ".venv", "artifacts"}
FORBIDDEN = [r"(?<![\w/])/(?:home|data|data2)/[A-Za-z0-9_-]+/",
             r"ghp_[A-Za-z0-9]{30,}", r"sk-[A-Za-z0-9]{30,}",
             r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
HTML_LINK = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
MD = MarkdownIt("commonmark").enable("table")


def slugs(text):
    """GitHub's heading anchors for a Markdown document."""
    found, seen = set(), {}
    tokens = MD.parse(text)
    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = "".join(c.content for c in tokens[i + 1].children or [] if c.type in ("text", "code_inline"))
        slug = re.sub(r"[^\w\- ]", "", title.strip().lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        found.add(slug if count == 0 else f"{slug}-{count}")
    return found


def markdown_links(text):
    for token in MD.parse(text):
        if token.type == "html_block":
            yield from HTML_LINK.findall(token.content)
        for child in token.children or []:
            if child.type == "link_open":
                yield child.attrGet("href")
            elif child.type == "image":
                yield child.attrGet("src")
            elif child.type == "html_inline":
                yield from HTML_LINK.findall(child.content)


def check_links(path, text, anchors):
    count = 0
    for link in markdown_links(text):
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        dest = (path.parent / unquote(url.path)).resolve() if url.path else path
        if not dest.is_relative_to(ROOT) or not dest.exists():
            raise ValueError(f"broken local link in {path.relative_to(ROOT)}: {link}")
        if url.fragment and dest.suffix == ".md":
            if dest not in anchors:
                anchors[dest] = slugs(dest.read_text())
            if unquote(url.fragment) not in anchors[dest]:
                raise ValueError(f"broken anchor in {path.relative_to(ROOT)}: {link}")
        count += 1
    return count


def check_files():
    entries = [p for p in ROOT.rglob("*") if not any(
        part in EXCLUDED or part.endswith(".egg-info") for part in p.relative_to(ROOT).parts)]
    for path in entries:
        if path.is_symlink():
            raise ValueError(f"symlink in release: {path.relative_to(ROOT)}")
    files = [p for p in entries if p.is_file()]
    links, anchors = 0, {}
    for path in files:
        if path.name.startswith(".env") or path.suffix in (".pem", ".key", ".pt", ".ckpt", ".npz"):
            raise ValueError(f"private/data artifact in release: {path.relative_to(ROOT)}")
        if path.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".toml", ".cff", ".csv"):
            text = path.read_text()
            for pattern in FORBIDDEN:
                if re.search(pattern, text):
                    raise ValueError(f"sensitive-pattern match in {path.relative_to(ROOT)}")
            if path.suffix == ".py":
                ast.parse(text, filename=str(path))
            if path.suffix in (".yaml", ".yml", ".cff"):
                yaml.safe_load(text)
            if path.suffix == ".md":
                links += check_links(path, text, anchors)
    return files, links


def check_provenance():
    for row in json.loads((ROOT / "results/manifest.json").read_text())["files"]:
        digest = hashlib.sha256((ROOT / row["file"]).read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"frozen result changed: {row['file']}")
    for filename, key, path_key in (("config_manifest.json", "configs", "file"),
                                    ("source_manifest.json", "files", "destination")):
        for row in json.loads((ROOT / "reproduce" / filename).read_text())[key]:
            path = (ROOT / row[path_key]).resolve()
            if not path.is_relative_to(ROOT):
                raise ValueError("manifest entry points outside release")
            if hashlib.sha256(path.read_bytes()).hexdigest() != row["public_sha256"]:
                raise ValueError(f"provenance hash changed: {row[path_key]}")


def check_workflows():
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text()
        if re.search(r"pull_request_target|self-hosted", text):
            raise ValueError("privileged/untrusted execution requires a separate security review")
        for action in re.findall(r"uses:\s*(\S+)", text):
            if not re.fullmatch(r"[\w-]+/[\w-]+@[0-9a-f]{40}", action):
                raise ValueError(f"action is not pinned: {action}")
    pages = yaml.safe_load((ROOT / ".github/workflows/pages.yml").read_text())
    if set(pages["on"]) != {"push", "workflow_dispatch"} or pages["on"]["push"]["branches"] != ["main"]:
        raise ValueError("pages.yml must deploy on pushes to main and on demand only")
    if "website/**" not in pages["on"]["push"]["paths"]:
        raise ValueError("pages.yml must deploy when website/ changes")
    if pages["permissions"] != {"contents": "read"}:
        raise ValueError("pages.yml must default to read-only permissions")
    jobs = pages["jobs"]
    if "default_branch" not in jobs["build"]["if"]:
        raise ValueError("pages.yml must deploy only from the default branch")
    if jobs["build"]["permissions"] != {"contents": "read", "pages": "read"}:
        raise ValueError("the Pages build job must be read-only")
    if jobs["deploy"]["permissions"] != {"pages": "write", "id-token": "write"}:
        raise ValueError("only the Pages deploy job may write")
    upload = [s for s in jobs["build"]["steps"] if "upload-pages-artifact" in s.get("uses", "")]
    if len(upload) != 1 or upload[0]["with"]["path"] != "website":
        raise ValueError("pages.yml must upload website/ and nothing else")
    validate_site(ROOT, "website")


def check_version():
    init = (ROOT / "src/pack3d/__init__.py").read_text()
    version = re.search(r'^__version__\s*=\s*"([^"]+)"', init, re.M).group(1)
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    if str(citation["version"]) != version:
        raise ValueError(f"CITATION.cff version {citation['version']} != package version {version}")
    if f"## [{version}]" not in (ROOT / "CHANGELOG.md").read_text():
        raise ValueError(f"CHANGELOG.md has no entry for {version}")
    if "MIT License" not in (ROOT / "LICENSE").read_text():
        raise ValueError("LICENSE is missing or is not the MIT License")
    return version


def check_script_versions():
    # each script the page loads carries ?v= and the first 8 hex digits of its SHA-256, so a browser
    # that cached an older copy fetches the one that matches the page it was sent with (docs/pages.md)
    page = (ROOT / "website/index.html").read_text()
    for name in ("d3.min.js", "app.js"):
        digest = hashlib.sha256((ROOT / "website" / name).read_bytes()).hexdigest()[:8]
        if f'src="{name}?v={digest}"' not in page:
            raise ValueError(f"website/index.html must load {name}?v={digest}")


def main():
    files, links = check_files()
    check_provenance()
    check_workflows()
    check_script_versions()
    version = check_version()
    print(f"PASS: {len(files)} files; {links} local links and anchors; provenance hashes; YAML; "
          f"pinned Actions; website workflow; script versions; version {version}")


if __name__ == "__main__":
    main()
