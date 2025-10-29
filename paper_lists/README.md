# paper_lists

## Directory Overview
- `downloaded_papers`: Lists of papers downloaded from each conference by `code/ai_papers_downloader`.
- `excluded_papers`: Lists of papers excluded from analysis because they were not part of the main technical track.
- `llm_evaluate`: Lists of papers evaluated by the `code/llm_evaluate` experiments. We divided up the papers in to 250 paper chunks for evaluation by the LLM. We ran `code/llm_evaluate` in 5 concurrent processes using the `.sh` scripts.