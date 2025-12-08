"""Mirror https://blog.sixhz.top/ into a static site directory using wget.

The script prefers the bundled wget on Windows (tools/mingw64/bin/wget.exe),
and uses the system wget on Linux/macOS, falling back to the bundled version
when system wget is unavailable. Output defaults to ./site and can be cleaned
before each run.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


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


if __name__ == "__main__":
    sys.exit(main())
