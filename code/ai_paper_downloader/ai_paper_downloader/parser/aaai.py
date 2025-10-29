#!/usr/bin/env python

from bs4 import BeautifulSoup


class AAAIParser:
    def __init__(self, html_file_path, year):
        self.html_file_path = html_file_path
        self.year = int(year)

        self.html_files = {
            2014: ["2014.html"],
            2015: ["2015.html"],
            2016: ["2016.html"],
            2017: ["2017.html"],
            2018: ["2018.html"],
            2019: ["2019.html"],
            2020: [
                "2020-track1.html",
                "2020-track2.html",
                "2020-track3.html",
                "2020-track4.html",
                "2020-track5.html",
                "2020-track6.html",
                "2020-track7.html",
            ],
            2021: [
                "2021-track1.html",
                "2021-track2.html",
                "2021-track3.html",
                "2021-track4.html",
                "2021-track5.html",
                "2021-track6.html",
                "2021-track7.html",
                "2021-track8.html",
                "2021-track9.html",
                "2021-track10.html",
                "2021-track11.html",
                "2021-track12.html",
                "2021-track13.html",
                "2021-track14.html",
                "2021-track15.html",
                "2021-track16.html",
            ],
            2022: [
                "2022-track1.html",
                "2022-track2.html",
                "2022-track3.html",
                "2022-track4.html",
                "2022-track5.html",
                "2022-track6.html",
                "2022-track7.html",
                "2022-track8.html",
                "2022-track9.html",
                "2022-track10.html",
            ],
            2023: [
                "2023-track1.html",
                "2023-track2.html",
                "2023-track3.html",
                "2023-track4.html",
                "2023-track5.html",
                "2023-track6.html",
                "2023-track7.html",
                "2023-track8.html",
                "2023-track9.html",
                "2023-track10.html",
                "2023-track11.html",
            ],
            2024: [
                "2024-track1.html",
                "2024-track2.html",
                "2024-track3.html",
                "2024-track4.html",
                "2024-track5.html",
                "2024-track6.html",
                "2024-track7.html",
                "2024-track8.html",
                "2024-track9.html",
                "2024-track10.html",
                "2024-track11.html",
                "2024-track12.html",
                "2024-track13.html",
                "2024-track14.html",
                "2024-track15.html",
                "2024-track16.html",
                "2024-track17.html",
                "2024-track18.html",
            ],
        }

    def parse_2014(self, html_file_path):
        # Load and parse the HTML file
        with open(html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers_metadata = []
        current_category = None

        # Flattened top-to-bottom walk of all tags
        for tag in soup.find_all(True):  # All tags, in order
            # Update category when we hit a track-wrap
            if tag.name == "div" and "track-wrap" in tag.get("class", []):
                h2 = tag.find("h2")
                current_category = h2.get_text(strip=True) if h2 else None

            # Extract paper when we hit a paper-wrap
            elif tag.name == "li" and "paper-wrap" in tag.get("class", []):
                title_tag = tag.find("h5")
                title = title_tag.get_text(strip=True) if title_tag else ""

                authors_tag = tag.find("span", class_="papers-author-page")
                authors = authors_tag.get_text(strip=True) if authors_tag else ""

                pdf_tag = tag.find("a", class_="wp-block-button")
                pdf_url = pdf_tag["href"] if pdf_tag and pdf_tag.has_attr("href") else ""

                papers_metadata.append({
                    "title": title,
                    "authors": authors,
                    "category": current_category,
                    "pdf_url": pdf_url,
                })



        return papers_metadata

    def parse_2023(self, html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers_metadata = []

        # Find all sections with categories
        sections = soup.find_all("div", class_="section")

        for section in sections:
            category = (
                section.find("h2").text.strip()
                if section.find("h2")
                else "Unknown Category"
            )

            # Find all articles in the section
            articles = section.find_all("div", class_="obj_article_summary")

            for article in articles:
                # Extract title
                title_tag = article.find("h3", class_="title").find("a")
                title = title_tag.text.strip() if title_tag else "Unknown Title"

                # Extract authors
                authors_tag = article.find("div", class_="authors")
                authors = authors_tag.text.strip() if authors_tag else "Unknown Authors"

                # Extract PDF URL
                pdf_tag = article.find("a", class_="obj_galley_link pdf")
                pdf_url = pdf_tag["href"] if pdf_tag else "No PDF available"

                papers_metadata.append(
                    {
                        "title": title,
                        "authors": authors,
                        "category": category,
                        "pdf_url": pdf_url,
                    }
                )

        return papers_metadata

    def parse(self):

        papers_metadata = []

        if self.year <= 2022:
            for html_file in self.html_files[self.year]:
                html_file_path = f"{self.html_file_path}/{html_file}"
                papers_metadata.extend(self.parse_2014(html_file_path))
        elif self.year >= 2023:
            for html_file in self.html_files[self.year]:
                html_file_path = f"{self.html_file_path}/{html_file}"
                papers_metadata.extend(self.parse_2023(html_file_path))

        return papers_metadata
