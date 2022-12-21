import re

from bs4 import BeautifulSoup

import nltk
from nltk.tokenize import word_tokenize

import difflib

# Extract text and image tags from an HTML document
def extract_text_and_tags(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    text = soup.get_text()
    image_tags = soup.find_all('img')
    return text, image_tags

# Tokenize the text and image tags
def tokenize(text, image_tags):
    text_tokens = word_tokenize(text)
    image_tokens = []
    for tag in image_tags:
        src = tag.get('src')
        alt = tag.get('alt')
        if src:
            image_tokens.extend(re.findall(r'\b\w+\b', src))
        if alt:
            image_tokens.extend(re.findall(r'\b\w+\b', alt))
    return text_tokens, image_tokens

# Create an index of the documents
def create_index(documents):
    nltk.download('punkt')
    
    index = {}
    for doc_id, doc in enumerate(documents):
        text, image_tags = extract_text_and_tags(doc)
        text_tokens, image_tokens = tokenize(text, image_tags)
        tokens = text_tokens + image_tokens
        for token in tokens:
            if token not in index:
                index[token] = []
            index[token].append(doc_id)
    return index

# Search the index for a given search term
def search(index, search_term, documents):
    search_tokens = word_tokenize(search_term)
    matching_doc_ids = []
    for token in search_tokens:
        if token in index:
            matching_doc_ids.extend(index[token])
    matching_doc_ids = list(set(matching_doc_ids))
    # Rank the documents based on how closely they match the search term
    ranked_docs = []
    for doc_id in matching_doc_ids:
        doc = documents[doc_id]
        similarity = difflib.SequenceMatcher(None, search_term, doc).ratio()
        ranked_docs.append((doc_id, similarity))
    ranked_docs.sort(key=lambda x: x[1], reverse=True)
    return [documents[doc_id] for doc_id, _ in ranked_docs]

# Test the search engine
documents = [
    '<html><body>This is a test document</body></html>',
    '<html><body>This is another test document</body></html>',
    '<html><body>This is a third test document</body></html>',
]
index = create_index(documents)
search_results = search(index, 'test document', documents)
print(search_results)  # Should print the three test documents
