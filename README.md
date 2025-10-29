# the-embrace-of-open-science

## Repository Overview

### code
- `code/ai_papers_downloader`: Scripts to download AI research papers from AAAI, ICLR, ICML, IJCAI, and NeurIPS for 2014 to 2024.
- `code/llm_evaluate`: Scripts used to evaluate the reproduciblity varaibles of the AI research papers using a large language model (LLM).
- `code/pdf_to_txt`: Utilities to convert PDF documents to plain text format for analysis by the LLM.  

### notebooks
- `notebooks/paper_count`: Jupyter notebook for Figure 1, which shows the number of papers downloaded from each conference for each year.
- `notebooks/raw_data`: Jupyter notebooks for processing raw data into csv files for analysis and verifying that all papers were evaluated by the LLM.
- `notebooks/results`: Jupyer notebook for analyzing the results from the LLM evaluation and creating the figures for the paper.
- `notebooks/SOTA`: Jupyter notebook for analysis of the LLM evaluation with the "State of the art: Reproducibility in artificial intelligence" from Gundersen and Kjensmo (2018) (the prompt optimization dataset).
- `notebooks/test_set`: Jupyter notebook for analyzing the LLM evaluation vs humman annotation with the randomized dataset of the whole population (the evaluation dataset).

### gundersen_2018
- Contains the ground truth for the prompt optimization dataset.

### paper_lists
- `paper_lists/downloaded_papers`: Lists of papers downloaded from each conference.
- `paper_lists/excluded_papers`: Lists of papers excluded from analysis because they were not part of the main technical track.
- `paper_lists/llm_evaluate`: Lists of papers selected for evaluation in the llm_evaluate experiments.

### prompts
- Contains the prompt sent to the LLM for evaluating the reproducibility variables in each paper.

### Results
- `results/evaluation`: Results from the the evaluation dataset to assess if the prompt created using the prompt optimization dataset (gundersen_2018) generlizes to the whole dataset.
- `results/experiment`: Results from evaluating the conference papers dataset.
- `results/prompt_optimization`: Results from the prompt optimization dataset (gundersen_2018) over 5 runs.

## Note about Reproducibility Variable Naming

In order to maintain consistenacy between the prompt optimization dataset (gundersen_2018) and the experiment results, we used the same names for reproducibility variables as used in the results from Gundersen and Kjensmo (`gundersen_2018/evaluations.csv`).
Therefore, for all results and analysis, the `train` JSON key and CSV column refers to the `open_source_code` reproducibility variable and the `validation` JSON key and CSV column refers to the `dataset_splits` reproducibility variable.