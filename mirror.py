"""Mirror https://blog.sixhz.top/ into a static site directory using wget.

The script prefers the bundled wget on Windows (tools/mingw64/bin/wget.exe),
and uses the system wget on Linux/macOS, falling back to the bundled version
when system wget is unavailable. Output defaults to ./site and can be cleaned
before each run.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen


DEFAULT_URL = "https://blog.sixhz.top/"
DEFAULT_OUTPUT_DIR = "site"
REJECT_REGEX = r"/(admin|login|register|action|feed)/"


def project_root() -> Path:
    """Return the directory containing this script."""
    return Path(__file__).resolve().parent


def resolve_output_dir(root: Path, output_dir: str) -> Path:
    """Resolve and validate the output directory inside the project root."""
    target = (root / output_dir).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("Output directory must stay under the project root") from exc
    return target


def bundled_wget_path(root: Path) -> Path:
    """Path to the repository-bundled wget executable."""
    return root / "tools" / "mingw64" / "bin" / "wget.exe"


def find_wget(root: Path) -> Path:
    """Pick the appropriate wget executable."""
    system_name = platform.system().lower()
    bundled = bundled_wget_path(root)
    system_wget = shutil.which("wget")

    if system_name == "windows":
        if bundled.exists():
            return bundled
        if system_wget:
            return Path(system_wget)
        raise FileNotFoundError(
            "wget not found. Expected bundled wget at tools/mingw64/bin/wget.exe "
            "or a system wget in PATH."
        )

    if system_wget:
        return Path(system_wget)
    if bundled.exists():
        return bundled
    raise FileNotFoundError(
        "wget not found. Install wget or place it at tools/mingw64/bin/wget.exe."
    )


def ensure_output_dir(output_dir: Path, clean: bool) -> None:
    """Create or clean the output directory."""
    if output_dir.exists() and clean:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def build_wget_command(
    wget_path: Path, output_dir: Path, url: str, spider: bool
) -> List[str]:
    """Construct the wget command for the mirror job."""
    command: List[str] = [
        str(wget_path),
        "--mirror",
        "--convert-links",
        "--adjust-extension",
        "--page-requisites",
        "--no-parent",
        f"--reject-regex={REJECT_REGEX}",
        "-P",
        str(output_dir),
        "-nH",
    ]
    if spider:
        command.append("--spider")
    command.append(url)
    return command


def stream_process_output(command: Iterable[str]) -> int:
    """Run a process and stream stdout/stderr to the console."""
    with subprocess.Popen(
        list(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    ) as proc:
        if proc.stdout:
            for line in proc.stdout:
                print(line, end="")
        return_code = proc.wait()
    return return_code


def rewrite_links_to_local(output_dir: Path, base_url: str) -> None:
    """Post-process downloaded files to point base-domain assets to local copies."""
    parsed = urlsplit(base_url)
    host = parsed.netloc
    if not host:
        return
    prefixes = {f"{scheme}://{host}" for scheme in ("http", "https")}
    prefixes.add(f"//{host}")
    pattern = re.compile(
        r"(?P<prefix>" + "|".join(re.escape(p) for p in prefixes) + r")(?P<path>/[^\s\"'>)]+)"
    )
    for file_path in output_dir.rglob("*"):
        if file_path.suffix.lower() not in {".html", ".htm", ".css", ".js"}:
            continue
        try:
            original = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        changed = False

        def _replace(match: re.Match[str]) -> str:
            nonlocal changed
            url_path = match.group("path")
            local_target = (output_dir / url_path.lstrip("/")).resolve()
            if local_target.exists():
                relative = Path(
                    os.path.relpath(local_target, start=file_path.parent.resolve())
                )
                changed = True
                return str(relative).replace("\\", "/")
            return match.group(0)

        rewritten = pattern.sub(_replace, original)
        if changed:
            try:
                file_path.write_text(rewritten, encoding="utf-8")
            except OSError:
                pass


def _hash_filename(url: str, default_ext: str = ".bin") -> str:
    parsed = urlsplit(url)
    ext = Path(parsed.path).suffix or default_ext
    digest = hashlib.sha1(url.encode("utf-8", "ignore")).hexdigest()
    return f"{digest}{ext}"


def download_external_images(output_dir: Path, base_url: str) -> None:
    """Download external img/src assets and rewrite HTML to local relative paths."""
    base_host = urlsplit(base_url).netloc
    external_dir = output_dir / "external_assets"
    external_dir.mkdir(parents=True, exist_ok=True)

    img_pattern = re.compile(
        r'(<img[^>]+src=["\'])(?P<src>https?:\/\/[^"\']+)(["\'])',
        flags=re.IGNORECASE,
    )
    replacements: dict[str, Path] = {}
    html_files = [
        p for p in output_dir.rglob("*") if p.suffix.lower() in {".html", ".htm"}
    ]

    for file_path in html_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        changed = False

        def _handle_match(match: re.Match[str]) -> str:
            nonlocal changed
            src_url = match.group("src")
            host = urlsplit(src_url).netloc
            if not host or host == base_host:
                return match.group(0)

            if src_url not in replacements:
                filename = _hash_filename(src_url, default_ext=".img")
                dest_path = external_dir / filename
                if not dest_path.exists():
                    try:
                        with urlopen(src_url, timeout=20) as resp, open(
                            dest_path, "wb"
                        ) as out_f:
                            shutil.copyfileobj(resp, out_f)
                    except (URLError, OSError):
                        return match.group(0)
                replacements[src_url] = dest_path

            dest_path = replacements[src_url]
            relative = Path(
                os.path.relpath(dest_path.resolve(), start=file_path.parent.resolve())
            )
            changed = True
            new_src = str(relative).replace("\\", "/")
            return f"{match.group(1)}{new_src}{match.group(3)}"

        rewritten = img_pattern.sub(_handle_match, content)
        if changed:
            try:
                file_path.write_text(rewritten, encoding="utf-8")
            except OSError:
                pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mirror https://blog.sixhz.top/ into a local static site directory."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Root URL to mirror (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory (relative to project root) to store the mirrored site (default: %(default)s)",
    )
    clean_group = parser.add_mutually_exclusive_group()
    clean_group.add_argument(
        "--clean",
        dest="clean",
        action="store_true",
        help="Remove the output directory before mirroring (default).",
    )
    clean_group.add_argument(
        "--no-clean",
        dest="clean",
        action="store_false",
        help="Keep existing output and download into it.",
    )
    parser.set_defaults(clean=True)
    parser.add_argument(
        "--spider",
        action="store_true",
        help="Use wget spider mode to test links without downloading files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = project_root()
    try:
        output_dir = resolve_output_dir(root, args.output_dir)
        ensure_output_dir(output_dir, clean=args.clean)
        wget_path = find_wget(root)
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Using wget at: {wget_path}")
    print(f"Output directory: {output_dir}")

    command = build_wget_command(wget_path, output_dir, args.url, args.spider)
    print("Running command:")
    print(" ".join(command))

    return_code = stream_process_output(command)
    if return_code != 0:
        print(f"wget exited with code {return_code}", file=sys.stderr)
        return return_code

    # Post-process links to ensure assets point to local copies for offline deploy.
    rewrite_links_to_local(output_dir, args.url)
    download_external_images(output_dir, args.url)
    return return_code


if __name__ == "__main__":
    sys.exit(main())
