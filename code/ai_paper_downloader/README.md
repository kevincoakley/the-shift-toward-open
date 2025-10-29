# ai_paper_downloader

A tool to download AI research papers from various AI conferences (AAAI, ICLR, ICML, IJCAI, NeurIPS).

## Installation (with uv)

1. Install [uv](https://github.com/astral-sh/uv):
   ```sh
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```
2. Install dependencies:
   ```sh
   uv pip install -r requirements.txt
   ```
   or, for editable install:
   ```sh
   uv pip install -e .
   ```

## Usage

Run the package as a module with the required arguments. Example:

```sh
python -m ai_paper_downloader --conference ICLR --year 2024 --save-dir papers
```

See `python -m ai_paper_downloader -h` for all available arguments.

## Notes
- For ICLR, you need an `openreview_pass.yaml` file with your OpenReview credentials.
- Compatible with [uv](https://github.com/astral-sh/uv) for fast dependency management.