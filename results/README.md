# results

## Directory Overview
- `evaluation/llm_eval.csv`: Results from the LLM of the 160 papers choosen at random to evaluate generalization of the prompt.
- `evaluation/manual_eval.csv`: Human evaluation of the 160 papers choosen at random to evaluate generalization of the prompt. Only the 9 reproducibility variables were evaluated by humans.
- `experiment/raw_data/`: The results of `code/llm_evaluate` for all of the papers from `paper_lists/llm_evaluate/`. The papers were evaluated in 250 paper chunks. The raw data includes the errors and reruns.
- `experiment/llm_results.csv`: The aggregated results from `experiment/raw_data/` to a csv file for analysis using `notebooks/raw_data/convert_json_results_to_csv.ipynb`.
- `prompt_optimization/raw_data/`: The results of `code/llm_evaluate` for the prompt optimization dataset from `paper_lists/llm_evaluate/`. The prompt optimization dataset was evaluated 5 times to analyze the variance in LLM responses. The raw data includes the errors and reruns.
- `prompt_optimization/results_run_{1-5}.csv`: The aggregated results from `prompt_optimization/raw_data/` to csv files for analysis using `notebooks/prompt_optimization/convert_json_results_to_csv.ipynb`.