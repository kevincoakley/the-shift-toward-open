#!/usr/bin/env python

from bs4 import BeautifulSoup


class NeurIPSParser:
    def __init__(self, html_file_path, year):
        self.html_file_path = html_file_path
        self.year = int(year)
        # Base URL for NeurIPS proceedings
        self.base_url = "https://proceedings.neurips.cc"

    def parse(self):
        # Load and parse the HTML file
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Find all paper links with title="paper title"
        papers = soup.find_all("a", title="paper title")

        papers_metadata = []

        # Process each paper link
        for paper in papers:
            parent_li = paper.find_parent("li")
            if not parent_li:
                continue  # Skip if the parent list item isn't found

            category = "None"

            if "conference" in parent_li.get("class", []):
                category = "conference"
            elif "datasets_and_benchmarks_track" in parent_li.get("class", []):
                category = "datasets_and_benchmarks_track"

            # Extract paper title and authors
            title = paper.text.strip()
            authors_tag = parent_li.find("i")
            authors = authors_tag.text.strip() if authors_tag else "Unknown"

            # Modify URL to point to the PDF file
            relative_url = paper["href"]
            pdf_url = self.base_url + relative_url.replace("hash", "file").replace(
                "-Abstract-Conference.html", "-Paper-Conference.pdf"
            ).replace(
                "-Abstract-Datasets_and_Benchmarks_Track.html",
                "-Paper-Datasets_and_Benchmarks_Track.pdf",
            ).replace(
                "-Abstract.html", "-Paper.pdf"
            )

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": category,
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata
