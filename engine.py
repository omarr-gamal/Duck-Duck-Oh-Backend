import re

import json

from bs4 import BeautifulSoup

import nltk
from nltk.tokenize import word_tokenize

import difflib

from models import Index, Document


class Engine:
    def __get_index(self):
        index = Index.query.first()
        if not index:
            index = Index('{}')
            index.insert()
        
        index_dict = json.loads(index.index)
        return index_dict

    def add_document(self, body):
        document = Document(body)
        document.insert()
        
        self.__index_document(Document)

    def __index_document(self, document):
        nltk.download('punkt')
        
        index = self.__get_index()
        
        text, image_tags = self.__extract_text_and_tags(document.body)
        text_tokens, image_tokens = self.__tokenize(text, image_tags)
        
        tokens = text_tokens + image_tokens
        
        for token in tokens:
            if token not in index:
                index[token] = []
            index[token].append(document.id)
        
        self.__update_index(index)

    def __update_index(self, index_dict):
        index_json = json.dumps(index_dict)
        
        index = Index.query.first()
        index.index = index_json
        
        index.update()

    # Extract text and image tags from an HTML document
    def __extract_text_and_tags(html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        text = soup.get_text()
        image_tags = soup.find_all('img')
        return text, image_tags

    # Tokenize the text and image tags
    def __tokenize(text, image_tags):
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

    # Search the index for a given search term
    def search(self, search_term, documents):
        index = self.__get_index()
        
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
# documents = [
#     '<html><body>This is a test document</body></html>',
#     '<html><body>This is another test document</body></html>',
#     '<html><body>This is a third test document</body></html>',
# ]
# index = create_index(documents)
# search_results = search(index, 'test document', documents)
# print(search_results)  # Should print the three test documents
