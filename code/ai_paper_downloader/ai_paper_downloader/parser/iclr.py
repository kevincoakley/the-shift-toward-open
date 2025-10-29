#!/usr/bin/env python

import openreview
from bs4 import BeautifulSoup
import yaml


class ICLRParser:
    def __init__(self, html_file_path, year):
        self.html_file_path = html_file_path
        self.year = int(year)
        self.arxiv_base_url = "https://arxiv.org/pdf/"

    def parse_openreview(self):
        # Load the configuration file
        with open("openreview_pass.yaml", "r") as yamlfile:
            credentials = yaml.safe_load(yamlfile)

        if int(self.year) >= 2024:
            # API V2
            print("Using API V2")
            API_VERSION = 2
            client = openreview.api.OpenReviewClient(
                baseurl='https://api2.openreview.net',
                username=credentials['username'],
                password=credentials['password']
            )
        else:
            # API V1
            print("Using API V1")
            API_VERSION = 1
            client = openreview.Client(
                baseurl='https://api.openreview.net',
                username=credentials['username'],
                password=credentials['password']
            )

        # Define the ICLR conference ID
        if int(self.year) >= 2018:
            conference_id = f"ICLR.cc/{self.year}/Conference"
        else:
            conference_id = f"ICLR.cc/{self.year}/conference"

        if API_VERSION == 2:
            # API V2: To only get "accepted" submissions, you'll need to query the notes by venueid
            submissions = client.get_all_notes(content={'venueid':conference_id} )
        elif API_VERSION == 1:
            # API V1
            # Fetch all **blind submissions** 
            if int(self.year) >= 2018:
                submissions = client.get_all_notes(invitation=f"{conference_id}/-/Blind_Submission", details='directReplies')
            else:
                submissions = client.get_notes(invitation=f"{conference_id}/-/submission")

        papers_metadata = []

        # Process each paper
        for paper in submissions:
            # Extract metadata
            if API_VERSION == 2:
                title = paper.content.get("title", {}).get("value", "No title")
                authors = ', '.join(paper.content.get("authors", {}).get("value", []))
                venue = paper.content.get("venue", {}).get("value", "No venue")
                pdf_url = f"https://openreview.net/pdf?id={paper.id}"
            elif API_VERSION == 1:
                title = paper.content.get("title", "No title")
                authors = ', '.join(paper.content.get("authors", []))
                venue = paper.content.get("venue", "No venue")
                pdf_url = f"https://openreview.net/pdf?id={paper.id}"

            # Set the category based on the venue and decision 
            # Skip papers that were not accepted
            category = "None"

            if API_VERSION == 1 and int(self.year) == 2017:
                if "poster" in venue.lower():
                    category = "poster"
                elif "oral" in venue.lower():
                    category = "oral"
                elif "spotlight" in venue.lower():
                    category = "spotlight" 
                elif "notable" in venue.lower():
                    category = "notable" 
                elif "submitted" in venue.lower():
                    continue  # Skip papers that were not accepted

            if API_VERSION == 1 and int(self.year) >= 2018:
                for reply in paper.details['directReplies']:
                    #print(reply)
                    print(title)
                    if "/Acceptance_Decision" in reply["invitation"]:
                        category = reply["content"]["decision"]
                    if "/Decision" in reply["invitation"]:
                        category = reply["content"]["decision"]
                    if "/Meta_Review" in reply["invitation"]:
                        category = reply["content"]["recommendation"]

                # Skip papers that were rejected
                if "reject" in category.lower():
                    continue
                elif category == "None":
                    print(f"Paper without category, skipping {title}")
                    continue

            if API_VERSION == 2:
                category = venue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": category,
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata


    def parse_2015_2016(self):
        with open(self.html_file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        papers_metadata = []
        
        sections = {
            "Oral Presentations": "oral",
            "Poster Presentations": "poster",
            "Main Conference - Oral Presentations": "oral",
            "Main Conference - Poster Presentations": "poster"
        }
        
        for section_title, category in sections.items():
            section = soup.find("h3", text=section_title)
            if section:
                paper_list = section.find_next("ol")
                if paper_list:
                    for li in paper_list.find_all("li"):
                        a = li.find("a")
                        if a and "arxiv.org" in a["href"]:
                            arxiv_id = a["href"].split("/")[-1]
                            title = a.text.strip()
                            authors = li.text.replace(title, "").strip()
                            authors = authors.replace("  ", " ")
                            authors = authors.replace("[code]\n", "")
                            authors = authors.removeprefix(", ")

                            papers_metadata.append(
                                {
                                    "title": title,
                                    "authors": authors,
                                    "category": category,
                                    "pdf_url": f"{self.arxiv_base_url}{arxiv_id}.pdf",
                                }
                            )

        return papers_metadata
    
    def parse_2014(self):
        with open(self.html_file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        papers_metadata = []
        seen_papers = set()  # Track papers already added

        # Define section headers and their font sizes
        oral_headers = ["Monday April 14:", "Tuesday April 15:", "Wednesday April 16:"]
        poster_header = "Conference Posters:"
        workshop_header = "Workshop Posters:"

        category = None  # Default category
        active_session = None  # Track which session is currently active

        for elem in soup.find_all(["font", "p"]):  # Only parse relevant elements
            text = elem.get_text().strip()
            link = elem.find("a", href=True)

            # Detect session headers based on font size
            if elem.name == "font" and "size" in elem.attrs:
                font_size = elem["size"]
                if font_size == "5" and text in oral_headers:
                    active_session = "oral"
                    continue
                elif font_size == "4" and text == poster_header:
                    active_session = "poster"
                    continue
                elif font_size == "4" and text == workshop_header:
                    active_session = "workshop"
                    continue

            # Identify and categorize papers (avoid duplicates)
            if link:
                title = link.get_text()
                url = link["href"]
                arxiv_id = url.split("/")[-1]

                # The authors are usually in the next paragraph
                authors_elem = elem.find_next_sibling("p")
                authors = authors_elem.get_text().strip() if authors_elem else "Unknown"

                # Create a unique identifier for each paper
                paper_id = (title, authors, arxiv_id)

                if paper_id not in seen_papers:  # Prevent duplicates
                    seen_papers.add(paper_id)
                    papers_metadata.append(
                        {
                            "title": title,
                            "authors": authors,
                            "category": active_session if active_session else "unknown",
                            "pdf_url": f"{self.arxiv_base_url}{arxiv_id}.pdf",
                        }
                    )

        return papers_metadata


    def parse(self):

        if self.year >= 2017:
            return self.parse_openreview()
        elif self.year == 2015 or self.year == 2016:
            return self.parse_2015_2016()
        elif self.year == 2014:
            return self.parse_2014()
        else:
            raise ValueError("Year not supported")