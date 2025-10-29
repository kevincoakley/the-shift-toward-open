import sys
import os
import csv
import requests
import time
from ai_paper_downloader import command_args
from ai_paper_downloader import generate_safe_filename
from ai_paper_downloader.parser.aaai import AAAIParser
from ai_paper_downloader.parser.iclr import ICLRParser
from ai_paper_downloader.parser.icml import ICMLParser
from ai_paper_downloader.parser.ijcai import IJCAIParser
from ai_paper_downloader.parser.neurips import NeurIPSParser


def main():
    # Parse the command line arguments
    args = command_args.args(sys.argv[1:])

    # Print the arguments
    print("========================================================================")
    print(
        f"Conference: {args.conference} Year: {args.year} Save Directory: {args.save_dir}"
    )
    print("========================================================================")

    # Define the directories and csv filename
    download_path = f"{args.save_dir}/{args.conference}/{args.year}"
    csv_file_path = f"{args.save_dir}/{args.conference}_{args.year}.csv"

    # Ensure directories exist
    os.makedirs(download_path, exist_ok=True)

    if args.conference == "AAAI":
        # Define the HTML file path
        html_file_path = f"static_html/{args.conference}"

        # Initialize the parser
        parser = AAAIParser(html_file_path, args.year)
    elif args.conference == "ICLR":
        # Define the HTML file path
        html_file_path = f"static_html/{args.conference}/{args.year}.html"

        # Initialize the parser
        parser = ICLRParser(html_file_path, args.year)
    elif args.conference == "ICML":
        # Define the HTML file path
        html_file_path = f"static_html/{args.conference}/{args.year}.html"

        # Initialize the parser
        parser = ICMLParser(html_file_path, args.year)
    elif args.conference == "IJCAI":
        # Define the HTML file path
        html_file_path = f"static_html/{args.conference}/{args.year}.html"

        # Initialize the parser
        parser = IJCAIParser(html_file_path, args.year)
    elif args.conference == "NeurIPS":
        # Define the HTML file path
        html_file_path = f"static_html/{args.conference}/{args.year}.html"

        # Initialize the parser
        parser = NeurIPSParser(html_file_path, args.year)

    # Get the list of papers from the conference
    papers = parser.parse()

    total_papers = len(papers)
    print(f"Total papers found: {total_papers}")

    if int(args.num_papers_to_download) != -1:
        num_papers_to_download = args.num_papers_to_download
    else:
        num_papers_to_download = total_papers

    # Define the CSV fields
    csv_fields = [
        "Conference",
        "Year",
        "Filename",
        "Title",
        "Authors",
        "Category",
        "PDF_URL",
    ]

    # Write CSV headers only if the file doesn't exist
    write_headers = not os.path.exists(csv_file_path)

    # Open CSV file for writing
    with open(csv_file_path, mode="a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write headers if file is new
        if write_headers:
            csv_writer.writerow(csv_fields)

        # Initialize the count
        count = 0

        # Open a log file for failed downloads
        failed_log_path = os.path.join(download_path, "failed_downloads.log")
        failed_log = open(failed_log_path, "a", encoding="utf-8")

        # Loop through the papers returned from the parser
        for paper in papers:
            # Generate a sanitized filename
            safe_filename = generate_safe_filename.generate_safe_filename(
                args.conference, args.year, paper["title"]
            )

            # Define PDF file path
            pdf_file_path = f"{download_path}/{safe_filename}"

            # Skip if the command line argument is set to skip downloads
            if args.no_download_pdf:
                # Skip download if file already exists
                if os.path.exists(pdf_file_path):
                    print(f"Skipping (already exists): {pdf_file_path}")
                    continue

                try:
                    # Set the user agent to avoid 403 errors
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                    }
                    """
                    # Download the PDF
                    response = requests.get(
                        paper["pdf_url"], headers=headers, stream=True
                    )
                    response.raise_for_status()
                    with open(pdf_file_path, "wb") as pdf_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            pdf_file.write(chunk)
                    """
                    print(
                        f"[{count+1}/{num_papers_to_download}] Downloaded: {paper['title']} -> {pdf_file_path}"
                    )

                    # Write to CSV
                    csv_writer.writerow(
                        [
                            args.conference,
                            args.year,
                            safe_filename,
                            paper["title"],
                            paper["authors"],
                            paper["category"],
                            paper["pdf_url"],
                        ]
                    )
                    csv_file.flush()  # Ensure data is written immediately

                    # Sleep to avoid overwhelming the server
                    time.sleep(int(args.seconds_between_downloads))
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download {paper['title']}: {e}")
                    failed_log.write(f"{paper['title']} | {paper['pdf_url']} | {e}\n")
                    failed_log.flush()
                    continue

            count += 1

            # Stop after downloading the specified number of papers
            if int(args.num_papers_to_download) != -1:
                if count >= int(num_papers_to_download):
                    break

    failed_log.close()
    csv_file.close()
    print("========================================================================")
    print(f"Papers Processed: {count}")
    print("========================================================================")
