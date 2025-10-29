#!/usr/bin/env python

import nltk
import spacy
from nltk.corpus import stopwords

# Download NLTK stopwords
nltk.download("stopwords")


def nlp_process(paper_text, filter_stopwords, lemmatize):

    # Load spaCy's English language model
    nlp = spacy.load("en_core_web_sm")

    # Convert text to lowercase
    paper_text = paper_text.lower()

    # Tokenize text using spaCy
    tokenized_paper_text = nlp(paper_text)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))

    if filter_stopwords == True and lemmatize == False:
        # Remove stopwords
        filtered_tokens = [
            token.text for token in tokenized_paper_text if token.text not in stop_words
        ]
    elif filter_stopwords == False and lemmatize == True:
        # Lemmatize text
        filtered_tokens = [token.lemma_ for token in tokenized_paper_text]
    elif filter_stopwords == True and lemmatize == True:
        # Remove stopwords and lemmatize text
        filtered_tokens = [
            token.lemma_
            for token in tokenized_paper_text
            if token.lemma_ not in stop_words
        ]

    # Join tokens back into a string
    cleaned_text = " ".join(filtered_tokens)

    return cleaned_text
