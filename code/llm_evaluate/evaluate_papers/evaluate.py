#!/usr/bin/env python

import csv
import json
import os
from sklearn.metrics import accuracy_score, f1_score


class Evaluate:

    def __init__(self, llm_results_file):
        self.llm_results_file = llm_results_file
        self.manual_results_file = "evaluations.json"
        self.model = ""

        self.filter_stopwords = None
        self.lemmatize = None
        self.permute = None
        self.random_seed = "random"

        self.num_papers = 0
        self.input_tokens = 0
        self.thoughts_tokens = 0
        self.output_tokens = 0
        self.cost = 0.0

        self.results_name = llm_results_file.split("/")[-1].split(".")[0]

        self.labels_to_evaluate = [
            "research_type",
            "result_outcome",
            "affiliation",
            "problem_description",
            "goal_objective",
            "research_method",
            "research_question",
            "hypothesis",
            "prediction",
            "contribution",
            "pseudocode",
            "open_source_code",
            "open_experiment_code",
            "train",
            "validation",
            "test",
            "results",
            "hardware_specification",
            "software_dependencies",
            "experiment_setup",
        ]

        self.metadata_columns = [
            "filter_stopwords",
            "lemmatize",
            "model",
            "permute",
            "prompt",
            "questions",
            "random_seed",
            "temperature",
            "top_p",
            "evaluation_seconds",
        ]

    def get_llm_eval_results(self, llm_results_file):
        # Load the LLM paper results
        llm_results = json.load(open(llm_results_file))

        # Get the metadata from the llm_results
        if "filter_stopwords" in llm_results:
            self.filter_stopwords = llm_results["filter_stopwords"]
        if "lemmatize" in llm_results:
            self.lemmatize = llm_results["lemmatize"]
        if "model" in llm_results:
            self.model = llm_results["model"]
        if "permute" in llm_results:
            self.permute = llm_results["permute"]
        if "random_seed" in llm_results:
            self.random_seed = llm_results["random_seed"]
        if "temperature" in llm_results:
            self.temperature = llm_results["temperature"]
        if "top_p" in llm_results:
            self.top_p = llm_results["top_p"]
        if "evaluation_seconds" in llm_results:
            self.evaluation_seconds = llm_results["evaluation_seconds"]

        # Remove the metadata from the llm_results
        for item in self.metadata_columns:
            if item in llm_results:
                llm_results.pop(item, None)

        return llm_results

    def get_manual_eval_results(self, manual_results_file):
        # Load the manual eval paper results
        manual_results_json = json.load(open(manual_results_file))

        #
        # Reformat the manual eval paper results to the paper_id as the key
        # to match the format of the llm results
        # #
        manual_results = {}

        for paper in manual_results_json:
            manual_results[str(paper["index"])] = paper

        return manual_results

    def evaluate_papers(self, llm_results, manual_results):
        llm_pred = []
        llm_pred_by_label = {}
        manual_true = []
        manual_true_by_label = {}

        # Loop through the llm results and get the papers (paper_id) that were evaluated
        for paper_id in llm_results.keys():
            # Loop through the labels in the llm results. Labels are the evaluation questions
            for label in llm_results[paper_id].keys():
                # Check if the label is in the list of labels to evaluate
                if label in self.labels_to_evaluate:

                    # Add the label to the llm_pred and manual_true lists if it doesn't exist
                    if label not in llm_pred_by_label:
                        llm_pred_by_label[label] = []
                    if label not in manual_true_by_label:
                        manual_true_by_label[label] = []

                    # Empty values in the csv file were set to -1, don't evaluate these
                    if manual_results[paper_id][label] == -1:
                        continue

                    # Check if the llm results can be converted to int
                    try:
                        int(llm_results[paper_id][label]["result"])
                    except TypeError:
                        print(f"Error converting {paper_id}: {label} to int")
                        continue

                    # Add the llm and manual results to the llm_pred and manual_true lists
                    llm_pred.append(int(llm_results[paper_id][label]["result"]))
                    llm_pred_by_label[label].append(int(llm_results[paper_id][label]["result"]))
                    manual_true.append(manual_results[paper_id][label])
                    manual_true_by_label[label].append(manual_results[paper_id][label])

            self.num_papers += 1
            self.input_tokens += llm_results[paper_id]["input_tokens"]
            self.thoughts_tokens += llm_results[paper_id]["thoughts_tokens"]
            self.output_tokens += llm_results[paper_id]["output_tokens"]
            self.cost += llm_results[paper_id]["cost"]

        return llm_pred, llm_pred_by_label, manual_true, manual_true_by_label

    def write_results(
        self, llm_pred, llm_pred_by_label, manual_true, manual_true_by_label
    ):
        csv_file = "evaluate_accuracy_results.csv"
        write_header = False
        write_result = True

        # if the csv file doesn't exist, write the header
        # else check if the results are already in the csv file and don't write them again
        if not os.path.isfile(csv_file):
            write_header = True
        else:
            with open(csv_file) as csvfile:
                if self.results_name in csvfile.read():
                    print("Results already in csv file")
                    write_result = False

        # Write the results to the csv file
        if write_result:
            with open(csv_file, "a") as csvfile:
                fieldnames = [
                    "results_name",
                    "model",
                    "evaluation_seconds",
                    "permute",
                    "filter_stopwords",
                    "lemmatize",
                    "random_seed",
                    "temperature",
                    "top_p",
                    "num_papers",
                    "average_input_tokens",
                    "average_thoughts_tokens",
                    "average_output_tokens",
                    "cost",
                    "research_type",
                    "result_outcome",
                    "affiliation",
                    "problem_description",
                    "goal_objective",
                    "research_method",
                    "research_question",
                    "hypothesis",
                    "prediction",
                    "contribution",
                    "pseudocode",
                    "open_source_code",
                    "open_experiment_code",
                    "train",
                    "validation",
                    "test",
                    "results",
                    "hardware_specification",
                    "software_dependencies",
                    "experiment_setup",
                    "total_accuracy",
                    "f1_score",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if write_header:
                    writer.writeheader()

                writer.writerow(
                    {
                        "results_name": self.results_name,
                        "model": self.model,
                        "evaluation_seconds": self.evaluation_seconds,
                        "permute": self.permute,
                        "filter_stopwords": self.filter_stopwords,
                        "lemmatize": self.lemmatize,
                        "random_seed": self.random_seed,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "num_papers": self.num_papers,
                        "average_input_tokens": self.input_tokens // self.num_papers,
                        "average_thoughts_tokens": self.thoughts_tokens // self.num_papers,
                        "average_output_tokens": self.output_tokens // self.num_papers,
                        "cost": round(self.cost, 4),
                        "research_type": round(accuracy_score(manual_true_by_label["research_type"], llm_pred_by_label["research_type"]), 4),
                        "result_outcome": round(accuracy_score(manual_true_by_label["result_outcome"], llm_pred_by_label["result_outcome"]), 4),
                        "affiliation": round(accuracy_score(manual_true_by_label["affiliation"], llm_pred_by_label["affiliation"]), 4),
                        "problem_description": round(accuracy_score(manual_true_by_label["problem_description"], llm_pred_by_label["problem_description"]), 4),
                        "goal_objective": round(accuracy_score(manual_true_by_label["goal_objective"], llm_pred_by_label["goal_objective"]), 4),
                        "research_method": round(accuracy_score(manual_true_by_label["research_method"], llm_pred_by_label["research_method"]), 4),
                        "research_question": round(accuracy_score(manual_true_by_label["research_question"], llm_pred_by_label["research_question"]), 4),
                        "hypothesis": round(accuracy_score(manual_true_by_label["hypothesis"], llm_pred_by_label["hypothesis"]), 4),
                        "prediction": round(accuracy_score(manual_true_by_label["prediction"], llm_pred_by_label["prediction"]), 4),
                        "contribution": round(accuracy_score(manual_true_by_label["contribution"], llm_pred_by_label["contribution"]), 4),
                        "pseudocode": round(accuracy_score(manual_true_by_label["pseudocode"], llm_pred_by_label["pseudocode"]), 4),
                        "open_source_code": round(accuracy_score(manual_true_by_label["open_source_code"], llm_pred_by_label["open_source_code"]), 4),
                        "open_experiment_code": round(accuracy_score(manual_true_by_label["open_experiment_code"], llm_pred_by_label["open_experiment_code"]), 4),
                        "train": round(accuracy_score(manual_true_by_label["train"], llm_pred_by_label["train"]), 4),
                        "validation": round(accuracy_score(manual_true_by_label["validation"], llm_pred_by_label["validation"]), 4),
                        "test": round(accuracy_score(manual_true_by_label["test"], llm_pred_by_label["test"]), 4),
                        "results": round(accuracy_score(manual_true_by_label["results"], llm_pred_by_label["results"]), 4),
                        "hardware_specification": round(accuracy_score(manual_true_by_label["hardware_specification"], llm_pred_by_label["hardware_specification"]), 4),
                        "software_dependencies": round(accuracy_score(manual_true_by_label["software_dependencies"], llm_pred_by_label["software_dependencies"]), 4),
                        "experiment_setup": round(accuracy_score(manual_true_by_label["experiment_setup"], llm_pred_by_label["experiment_setup"]), 4),
                        "total_accuracy": round(accuracy_score(manual_true, llm_pred), 4),
                        "f1_score": round(f1_score(manual_true, llm_pred, average="macro"), 4),
                    }
                )

    def evaluate_accuracy(self):

        llm_results = self.get_llm_eval_results(self.llm_results_file)
        manual_results = self.get_manual_eval_results(self.manual_results_file)

        llm_pred, llm_pred_by_label, manual_true, manual_true_by_label = (
            self.evaluate_papers(llm_results, manual_results)
        )

        self.write_results(
            llm_pred, llm_pred_by_label, manual_true, manual_true_by_label
        )
