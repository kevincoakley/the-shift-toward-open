# Main script for evaluating papers using LLMs
import sys
from datetime import datetime
import json
import random
import time
import yaml
import os

import evaluate_papers.args as args
from evaluate_papers.evaluate import Evaluate
from evaluate_papers.llm.chatgpt import ChatGPTAzure
from evaluate_papers.llm.chatgpt import ChatGPTOpenAI
from evaluate_papers.llm.chatgpt import ChatGPTCompatibleService
from evaluate_papers.llm.claude import ClaudeAnthropic
from evaluate_papers.llm.claude import ClaudeAWS
from evaluate_papers.llm.gemini import GeminiText
from evaluate_papers.llm.gemini import GeminiMultimodal
from evaluate_papers.llm.gemini import GeminiVertexText
from evaluate_papers.llm.gemini import GeminiVertexMultimodal
from evaluate_papers.llm.vertex_maas import VertexMaaS
from evaluate_papers.llm.ollama import Ollama
import evaluate_papers.nlp as nlp
import evaluate_papers.permute as permute


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Parse the command line arguments
    parsed_args = args.args(argv)

    # Set the random seed
    if parsed_args.random_seed != 0:
        random.seed(parsed_args.random_seed)

    # Read the configuration file
    with open(parsed_args.config_file) as f:
        config = yaml.safe_load(f)

    # Configure LLM client
    llm_client = None
    if config["llm"] == "chatgpt-azure":
        llm_client = ChatGPTAzure(
            config["api_key"],
            config["azure_endpoint"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "chatgpt-openai":
        llm_client = ChatGPTOpenAI(
            config["api_key"],
            config["organization"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "chatgpt-compatible-service":
        llm_client = ChatGPTCompatibleService(
            config["api_key"],
            config["base_url"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "claude-anthropic":
        llm_client = ClaudeAnthropic(
            config["api_key"],
            config["model"]["name"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "claude-aws":
        llm_client = ClaudeAWS(
            config["aws_access_key"],
            config["aws_secret_key"],
            config["aws_region"],
            config["model"]["name"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "gemini-text":
        llm_client = GeminiText(
            config["api_key"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "gemini-multimodal":
        llm_client = GeminiMultimodal(
            config["api_key"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "gemini-vertex-text":
        llm_client = GeminiVertexText(
            config["project_id"],
            config["region"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "gemini-vertex-multimodal":
        llm_client = GeminiVertexMultimodal(
            config["project_id"],
            config["region"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "vertex-maas":
        llm_client = VertexMaaS(
            config["project_id"],
            config["region"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    elif config["llm"] == "ollama":
        llm_client = Ollama(
            config["host"],
            config["model"]["name"],
            config["structured_output"],
            parsed_args.temperature,
            parsed_args.top_p,
        )
    else:
        print(f"Unknown LLM type: {config['llm']}")
        sys.exit(1)

    # Read the prompt
    with open("prompt.txt", "r") as file:
        prompt = file.read()

    # Read the questions from the questions.yaml file
    with open(parsed_args.questions_file) as f:
        questions_yaml = yaml.safe_load(f)

    # Create the questions string
    questions = questions_yaml["prompt"] + "\n\n"
    for question in questions_yaml["questions"]:
        questions += question["question"] + " " + question["return"] + "\n"

    # Evaluate papers with the LLM
    results = {}
    errors = {}

    # Evaluate either all papers or just the test papers
    if parsed_args.papers_to_evaluate == "all":
        paper_ids_to_evaluate = [
            str(paper["index"]) for paper in json.load(open("evaluations.json"))
        ]
    else:
        # Check if parsed_args.papers_to_evaluate exists
        try:
            with open(parsed_args.papers_to_evaluate, "r") as file:
                paper_ids_to_evaluate = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"File not found: {parsed_args.papers_to_evaluate}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            sys.exit(1)

    papers_path = parsed_args.papers_path

    # Check if the papers path exists
    if not os.path.exists(papers_path):
        print(f"Papers path does not exist: {papers_path}")
        sys.exit(1)
    
    # Remove trailing slashes from the papers path
    papers_path = papers_path.rstrip("/")

    # Time the evaluation
    start_time = datetime.now()

    for paper_id in paper_ids_to_evaluate:
        print(f"Processing paper {paper_id}")
        
        # Read the paper text
        try:
            with open(f"{papers_path}/{paper_id}.txt", "r", encoding="utf-8") as file:
                paper_text = file.read()
            paper_text = paper_text.replace("- ", "")
        except Exception as e:
            print(f"Error processing paper {paper_id}: {e}")
            errors[paper_id] = str(e)
            continue

        # Permute the paper text
        if parsed_args.permute == "none":
            pass
        elif parsed_args.permute == "paragraph":
            paper_text = permute.permute_paper(paper_text, split="paragraph")
        elif parsed_args.permute == "sentence":
            paper_text = permute.permute_paper(paper_text, split="sentence")

        # Remove stopwords and lemmatize the paper text
        if parsed_args.filter_stopwords or parsed_args.lemmatize:
            paper_text = nlp.nlp_process(
                paper_text, parsed_args.filter_stopwords, parsed_args.lemmatize
            )

        try:
            # Evaluate the paper with the LLM
            paper_results, input_tokens, thoughts_tokens, output_tokens = llm_client.evaluate_papers(
                paper_id, prompt, paper_text, questions
            )
        except Exception as e:
            print(f"Error processing paper {paper_id}: {e}")
            errors[paper_id] = str(e)
            continue

        input_cost = (input_tokens / 1_000_000) * config["model"]["input_cost"]
        thoughts_cost = (thoughts_tokens / 1_000_000) * config["model"]["output_cost"]
        output_cost = (output_tokens / 1_000_000) * config["model"]["output_cost"]

        try:
            results[paper_id] = json.loads(paper_results)
            results[paper_id]["input_tokens"] = input_tokens
            results[paper_id]["thoughts_tokens"] = thoughts_tokens
            results[paper_id]["output_tokens"] = output_tokens
            results[paper_id]["cost"] = round(input_cost + thoughts_cost + output_cost, 6)
        except (ValueError, TypeError):
            print(f"Error {paper_id}: ")
            print(paper_results)
            errors[paper_id] = paper_results

        # Save the results to a file after each paper is processed
        results_filename = save_results(
            results, errors, start_time, parsed_args, config, prompt, questions, llm_client.results_filename
        )

        if parsed_args.rate_limit > 0:
            time.sleep(parsed_args.rate_limit)

    # If evaluate flag is set, evaluate the accuracy of the results
    if parsed_args.evaluate:
        llm_eval = Evaluate(results_filename)
        llm_eval.evaluate_accuracy()

def save_results(results, errors, start_time, parsed_args, config,prompt, questions, llm_results_filename):
    ###
    end_time = datetime.now()
    evaluation_time = end_time - start_time

    results_save = results.copy()
    errors_save = errors.copy()

    results_save["filter_stopwords"] = parsed_args.filter_stopwords
    results_save["lemmatize"] = parsed_args.lemmatize
    results_save["model"] = config["model"]["name"]
    results_save["permute"] = parsed_args.permute
    results_save["prompt"] = prompt
    results_save["questions"] = questions
    if parsed_args.random_seed != 0:
        results_save["random_seed"] = parsed_args.random_seed
    results_save["temperature"] = parsed_args.temperature
    results_save["top_p"] = parsed_args.top_p
    results_save["evaluation_seconds"] = str(int(evaluation_time.total_seconds()))

    if parsed_args.results_filename != "":
        results_filename = parsed_args.results_filename
    else:
        results_filename = llm_results_filename % start_time.strftime("%Y-%m-%d-%H-%M-%S")

    with open(results_filename, "w", encoding="utf-8") as f:
        json.dump(results_save, f, ensure_ascii=False, indent=4)
    print("Results saved to %s" % results_filename)

    if len(errors) > 0:
        errors_save["model"] = config["model"]
        errors_save["prompt"] = prompt
        errors_save["questions"] = questions
        
        if parsed_args.results_filename != "":
            errors_filename = parsed_args.results_filename + ".errors"
        else:
            errors_filename = llm_results_filename % start_time.strftime("%Y-%m-%d-%H-%M-%S") + ".errors"

        with open(errors_filename, "w", encoding="utf-8") as f:
            json.dump(errors_save, f, ensure_ascii=False, indent=4)
        print("Errors saved to %s" % errors_filename)

    return results_filename


if __name__ == "__main__":
    sys.exit(main())
