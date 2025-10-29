#!/usr/bin/env python

from bs4 import BeautifulSoup


class ICMLParser:
    def __init__(self, html_file_path, year):
        self.html_file_path = html_file_path
        self.year = int(year)

    def parse(self):

        # Read the HTML file
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Find all papers
        papers = soup.find_all("div", class_="paper")

        papers_metadata = []

        for paper in papers:
            # Extract title
            title_tag = paper.find("p", class_="title")
            title = title_tag.text.strip() if title_tag else "Unknown"

            # Extract authors
            authors_tag = paper.find("span", class_="authors")
            authors = (
                authors_tag.text.strip().replace("\xa0", " ")
                if authors_tag
                else "Unknown"
            )

            # Extract PDF link
            pdf_link_tag = paper.find("a", text="Download PDF")
            pdf_url = pdf_link_tag["href"] if pdf_link_tag else None

            category = "None"

            if not pdf_url:
                print(f"Skipping: No PDF found for {title}")
                continue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": category,
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata
