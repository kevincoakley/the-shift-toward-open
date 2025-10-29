#!/usr/bin/env python

import argparse


def args(args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--conference",
        dest="conference",
        help="Conference name to download papers from",
        default="none",
        choices=[
            "AAAI",
            "ICLR",
            "ICML",
            "IJCAI",
            "NeurIPS",
        ],
        required=True,
    )

    parser.add_argument(
        "--year",
        dest="year",
        help="Year of the conference",
        default="none",
        choices=[
            "2024",
            "2023",
            "2022",
            "2021",
            "2020",
            "2019",
            "2018",
            "2017",
            "2016",
            "2015",
            "2014",
        ],
        required=True,
    )

    parser.add_argument(
        "--save-dir",
        dest="save_dir",
        help="The directory to save the papers",
        default="papers",
        required=False,
    )

    parser.add_argument(
        "--num-papers-to-download",
        dest="num_papers_to_download",
        help="The number of papers to download",
        default=-1,
        required=False,
    )

    parser.add_argument(
        "--no-download-pdf",
        dest="no_download_pdf",
        help="Don't download the PDFs of the papers",
        action="store_false",
        required=False,
    )

    parser.add_argument(
        "--seconds-between-downloads",
        dest="seconds_between_downloads",
        help="The number of seconds to wait between downloading papers",
        default=1,
        required=False,
    )

    return parser.parse_args(args)
