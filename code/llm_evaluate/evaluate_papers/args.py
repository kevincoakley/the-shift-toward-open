#!/usr/bin/env python

import argparse


def args(args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        dest="config_file",
        help="Configuration file for the LLM service to use for evaluation.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--temperature",
        dest="temperature",
        help="Temperature for LLM response generation.",
        type=float,
        default=-1,
        required=False,
    )

    parser.add_argument(
        "--top-p",
        dest="top_p",
        help="Top-P for LLM response generation.",
        type=float,
        default=-1,
        required=False,
    )

    parser.add_argument(
        "--questions",
        dest="questions_file",
        help="Yaml file containing the questions to ask the LLM.",
        default="questions.yaml",
        type=str,
        required=False,
    )

    parser.add_argument(
        "--papers",
        dest="papers_to_evaluate",
        help="Evaluate test papers or all papers.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--papers-path",
        dest="papers_path",
        help="Path to the directory containing the papers to evaluate.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--results-filename",
        dest="results_filename",
        help="Path of the file where the results are saved.",
        type=str,
        default="",
        required=False,
    )

    parser.add_argument(
        "--permute",
        dest="permute",
        help="How to permute the paper text.",
        default="none",
        choices=[
            "paragraph",
            "sentence",
        ],
        required=False,
    )

    parser.add_argument(
        "--filter-stopwords",
        dest="filter_stopwords",
        help="Remove stop words from paper text.",
        action="store_true",
        required=False,
    )

    parser.add_argument(
        "--lemmatize",
        dest="lemmatize",
        help="Lemmatize paper text.",
        action="store_true",
        required=False,
    )

    parser.add_argument(
        "--rate-limit",
        dest="rate_limit",
        help="Number of seconds to pause between LLM queries.",
        type=int,
        default=0,
        required=False,
    )

    parser.add_argument(
        "--random-seed",
        dest="random_seed",
        help="Set the random seed for reproducibility.",
        type=int,
        default=0,
        required=False,
    )

    parser.add_argument(
        "--evaluate",
        dest="evaluate",
        help="Evaluate the model on the test set.",
        action="store_true",
        required=False,
    )

    return parser.parse_args(args)
