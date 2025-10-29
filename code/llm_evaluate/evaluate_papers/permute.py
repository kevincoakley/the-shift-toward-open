#!/usr/bin/env python

import random

def permute_paper(paper_text, split="paragraph"):

    # Split into paragraphs
    paper_list = paper_text.split("\n")

    if split == "paragraph":
        pass
    elif split == "sentence":
        # Split into sentences
        paper_list = [item.strip() for line in paper_list for item in line.replace(". ", ".. ").split(". ") if item.strip()]
    else:
        raise ValueError("split must be 'paragraph' or 'sentence'")

    # Remove strings with two words or less
    paper_list = [s for s in paper_list if len(s.split()) > 2]

    # Shuffle the list
    random.shuffle(paper_list)

    # Return the permuted paper as a string
    return '\n'.join(paper_list) + '\n'