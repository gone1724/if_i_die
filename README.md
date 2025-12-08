# if_i_die

Mirror https://blog.sixhz.top/ into a static site directory using wget.

## Usage
- Ensure Python 3.9+ is available; uv can be used to run the script without a venv.
- Run: `uv run python mirror.py` (or `python mirror.py` if you prefer).
- Options:
  - `--no-clean` to keep existing files in `site/`.
  - `--spider` to test the crawl without downloading.
  - `--url` and `--output-dir` to override defaults.
- The script prefers the bundled `tools/mingw64/bin/wget.exe` on Windows, otherwise system `wget`.
