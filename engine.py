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
    
    def __update_index(self, index_dict):
        index_json = json.dumps(index_dict)
        
        index = Index.query.first()
        index.index = index_json
        
        index.update()

    def add_document(self, body):
        document = Document(body=body)
        document.insert()
        
        self.__index_document(document)

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

    # Extract text and image tags from an HTML document
    def __extract_text_and_tags(self, html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        text = soup.get_text()
        image_tags = soup.find_all('img')
        return text, image_tags

    # Tokenize the text and image tags
    def __tokenize(self, text, image_tags):
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
    
    def search(self, search_term):
        # Tokenize the search term
        search_tokens = word_tokenize(search_term)
        # Initialize a set to keep track of the documents that contain all the tokens in the search term
        matching_documents = set()
        # Iterate over the tokens in the search term
        for token in search_tokens:
            # Get the documents that contain the current token
            documents = self.__get_index().get(token, [])
            # If this is the first token, initialize the matching_documents set with the documents that contain the token
            if not matching_documents:
                matching_documents = set(documents)
            # Otherwise, update the matching_documents set to only include documents that contain all the tokens in the search term
            else:
                matching_documents &= set(documents)
        # Rank the documents based on how closely they match the search term
        ranked_documents = sorted(matching_documents, key=lambda doc_id: self.__rank_document(doc_id, search_term))
        # Return the ranked document ids
        return ranked_documents
    
    def __rank_document(self, doc_id, search_term):
        # Fetch the document with the given id
        document = Document.query.get(doc_id)
        # Tokenize the document
        nltk.download('punkt')
        text, image_tags = self.__extract_text_and_tags(document.body)
        text_tokens, image_tokens = self.__tokenize(text, image_tags)
        tokens = text_tokens + image_tokens
        # Tokenize the search term
        search_tokens = word_tokenize(search_term)
        # Initialize a count to keep track of the number of occurrences of the search term in the document
        count = 0
        # Iterate over the tokens in the document
        for i, token in enumerate(tokens):
            # Check if the current token is the first token in the search term
            if token == search_tokens[0]:
                # Check if the remaining tokens in the document match the search term
                if tokens[i:i+len(search_tokens)] == search_tokens:
                    count += 1
        # Return the count as the rank
        return count
