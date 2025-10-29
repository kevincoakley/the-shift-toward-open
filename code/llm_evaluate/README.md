# llm_evaluate

## Before you start


### 1. Create Python environment using [uv](https://github.com/astral-sh/uv)

Install `uv` if you don't have it:

    pip install uv

Create and sync the environment:

    uv venv .venv
    uv pip install -r requirements.txt

Activate the environment:

    source .venv/bin/activate

Download spaCy model:

    python -m spacy download en_core_web_sm

### 2. Create a config file

Copy a config template from `config_examples/` and update it with your model name and api key if needed.

### 3. Copy the txt version of the papers to the papers/ directory

1. State of the Art: Reproducibility in Artificial Intelligence Papers (prompt optimization dataset) are listed in `gundersen_2018/evaluations.csv` and must be named using the index and .txt extension (e.g., `1.txt`, `2.txt`, etc.).

2. The conference papers dataset can be downloaded using `code/ai_papers_downloader`.

3. The PDFs can be converted to txt using `code/pdf_to_txt`

## Evaluate Papers

### Evaluate the State of the Art: Reproducibility in Artificial Intelligence (Prompt Optimization Dataset) Papers


    python -m evaluate_papers --config config.yaml --papers all --papers-path papers/ --results-filename sota.json --evaluate

### Evaluate Conference Papers

    python -m evaluate_papers --config config.yaml --papers paper_lists.json --papers-path papers/ --results-filename paper_results.json

Papers lists used in the experiment are in `/paper_lists/llm_evaluate/`

## Google Gemini Vertex Login

gcloud auth list
gcloud auth login <account_email>
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform
gcloud config set project <project_id>
