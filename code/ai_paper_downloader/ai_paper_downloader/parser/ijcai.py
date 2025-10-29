#!/usr/bin/env python

from bs4 import BeautifulSoup
import os

class IJCAIParser:
    def __init__(self, html_file_path, year):
        self.html_file_path = html_file_path
        self.year = int(year)

    def parse(self):
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers_metadata = []

        # Check for new style (2017+) with div.section
        sections = soup.find_all("div", class_="section")
        if sections:
            # New style (2017+)
            for section in sections:
                section_title_div = section.find("div", class_="section_title")
                if section_title_div and section_title_div.find("h3"):
                    track_name = section_title_div.find("h3").get_text(strip=True)
                else:
                    track_name = "Unknown"

                for subsection in section.find_all("div", class_="subsection"):
                    subsection_title_div = subsection.find("div", class_="subsection_title")
                    if subsection_title_div:
                        category = subsection_title_div.get_text(strip=True)
                    else:
                        category = track_name

                    for paper in subsection.find_all("div", class_="paper_wrapper"):
                        title_tag = paper.find("div", class_="title")
                        title = title_tag.get_text(strip=True) if title_tag else "Unknown"

                        authors_tag = paper.find("div", class_="authors")
                        authors = authors_tag.get_text(strip=True) if authors_tag else "Unknown"

                        details_div = paper.find("div", class_="details")
                        pdf_url = None
                        if details_div:
                            pdf_link = details_div.find("a", string="PDF")
                            if pdf_link and pdf_link.get("href"):
                                href = pdf_link["href"]
                                if href.startswith("http"):
                                    pdf_url = href
                                else:
                                    base_url = f"https://www.ijcai.org/proceedings/{self.year}/"
                                    pdf_url = os.path.join(base_url, href)
                        if not pdf_url:
                            continue
                        papers_metadata.append({
                            "title": title,
                            "authors": authors,
                            "category": category,
                            "pdf_url": pdf_url,
                        })
        else:
            # Old style (2015/2016): <h3> for category, <p> for each paper
            last_category = None
            collecting = False
            for tag in soup.find_all(["h3", "p"]):
                if tag.name == "h3":
                    txt = tag.get_text(strip=True)
                    if txt.lower().startswith("edited by") or "sponsor" in txt.lower() or "published by" in txt.lower():
                        continue
                    last_category = txt
                    collecting = True
                elif tag.name == "p":
                    # Accept papers before any <h3> as 'Main Track'
                    if not collecting or not last_category:
                        # Try to detect a paper anyway if it looks like a paper entry
                        contents = tag.contents
                        if len(contents) < 5:
                            continue
                        if isinstance(contents[0], str):
                            title_part = contents[0].strip()
                            if "/" in title_part:
                                title = title_part.split("/")[0].strip()
                            else:
                                title = title_part
                        else:
                            continue
                        authors = "Unknown"
                        # Try <em> first (IJCAI 2015), then <i> (IJCAI 2016)
                        for c in contents:
                            if getattr(c, 'name', None) == "em":
                                authors = c.get_text(strip=True)
                                break
                        if authors == "Unknown":
                            for c in contents:
                                if getattr(c, 'name', None) == "i":
                                    authors = c.get_text(strip=True)
                                    break
                        pdf_url = None
                        for a in tag.find_all("a"):
                            if a.get_text(strip=True).upper() == "PDF" and a.get("href"):
                                href = a["href"]
                                if href.startswith("http"):
                                    pdf_url = href
                                else:
                                    pdf_url = f"https://www.ijcai.org{href}"
                                break
                        if not pdf_url or not title or not authors:
                            continue
                        papers_metadata.append({
                            "title": title,
                            "authors": authors,
                            "category": "Main Track",
                            "pdf_url": pdf_url,
                        })
                        continue
                    # Normal case: after first <h3>
                    contents = tag.contents
                    if len(contents) < 5:
                        continue
                    if isinstance(contents[0], str):
                        title_part = contents[0].strip()
                        if "/" in title_part:
                            title = title_part.split("/")[0].strip()
                        else:
                            title = title_part
                    else:
                        continue
                    authors = "Unknown"
                    # Try <em> first (IJCAI 2015), then <i> (IJCAI 2016)
                    for c in contents:
                        if getattr(c, 'name', None) == "em":
                            authors = c.get_text(strip=True)
                            break
                    if authors == "Unknown":
                        for c in contents:
                            if getattr(c, 'name', None) == "i":
                                authors = c.get_text(strip=True)
                                break
                    pdf_url = None
                    for a in tag.find_all("a"):
                        if a.get_text(strip=True).upper() == "PDF" and a.get("href"):
                            href = a["href"]
                            if href.startswith("http"):
                                pdf_url = href
                            else:
                                pdf_url = f"https://www.ijcai.org{href}"
                            break
                    if not pdf_url or not title or not authors or not last_category:
                        continue
                    papers_metadata.append({
                        "title": title,
                        "authors": authors,
                        "category": last_category,
                        "pdf_url": pdf_url,
                    })

        # Deduplicate papers by PDF URL (for 2020+)
        unique = {}
        for paper in papers_metadata:
            key = paper["pdf_url"]
            if key not in unique:
                unique[key] = paper

        return list(unique.values())