import re

import json

from bs4 import BeautifulSoup

import nltk

from .models import Index, Document
from .extensions import db

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Engine:
    def __init__(self):
        self.__is_initialized = False

    def download_nltk_dicts(self):
        nltk.download("punkt")
        nltk.download("punkt_tab")
        nltk.download("stopwords")

    def __initialize(self):
        if self.__is_initialized:
            return

        self.download_nltk_dicts()

        self.stop_words = list(nltk.corpus.stopwords.words("english"))
        self.vectorizer = TfidfVectorizer(stop_words=self.stop_words)

        self.index = {}
        self.documents = [document.body for document in Document.query.all()]

        # Set initialized to True early to prevent recursion when calling index_all_documents
        self.__is_initialized = True

        ind = Index.query.first()
        try:
            if ind and ind.index:
                self.index = json.loads(ind.index)
            else:
                raise ValueError("Empty index")
        except (json.JSONDecodeError, ValueError):
            self.index = {}
            if not ind:
                ind = Index("{}")
                ind.insert()
            
            self.index_all_documents()
        
        if self.documents:
            self.vectorizer.fit(self.documents)

    def index_all_documents(self):
        self.__initialize()

        for document in Document.query.all():
            tokens = self.__tokenize(document.body)
            self.__add_to_index(document.id, tokens)

    def __update_index(self):
        index_json = json.dumps(self.index)

        index = Index.query.first()
        index.index = index_json

        index.update()

    def __tokenize(self, body):
        # HTML syntax, special characters, \n and \r
        body = re.sub(r"<[^>]*>", "", body)
        body = re.sub(r"[^\w\s]", "", body)
        body = body.replace("\n", "").replace("\r", "")

        tokens = nltk.word_tokenize(body)
        tokens = [token for token in tokens if token not in self.stop_words]

        stemmer = nltk.stem.PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]

        return tokens

    def __add_to_index(self, document_id, tokens):
        for token in tokens:
            if token in self.index:
                self.index[token].append(document_id)
            else:
                self.index[token] = [document_id]

        self.__update_index()

    def add_document(self, body):
        self.__initialize()

        document = Document(body)
        document.insert()

        self.documents.append(body)

        tokens = self.__tokenize(body)
        self.__add_to_index(document.id, tokens)

        self.vectorizer.fit(self.documents)

        return document

    def __search_index(self, search_term):
        search_tokens = self.__tokenize(search_term)

        matching_documents = []
        for token in search_tokens:
            if token in self.index:
                matching_documents += self.index[token]

        matching_documents = list(set(matching_documents))

        return matching_documents

    def __rank_results(self, documents, search_term):
        if not len(documents) or not search_term:
            return []

        bodies = []
        valid_documents = []
        for document_id in documents:
            doc = db.session.get(Document, document_id)
            if doc:
                bodies.append(doc.body)
                valid_documents.append(document_id)
        
        if not bodies:
            return []

        search_vector = self.vectorizer.transform([search_term])
        document_vectors = self.vectorizer.transform(bodies)

        similarities = [
            cosine_similarity(search_vector, document_vector)[0][0]
            for document_vector in document_vectors
        ]
        ranked_documents = [
            document
            for _, document in sorted(zip(similarities, valid_documents), reverse=True)
        ]

        return ranked_documents

    def search(self, search_term):
        self.__initialize()

        documents = self.__search_index(search_term)
        ranked_documents = self.__rank_results(documents, search_term)

        return ranked_documents

    def search_images(self, search_term):
        self.__initialize()

        matching_documents = self.__search_index(search_term)
        ranked_documents = self.__rank_results(matching_documents, search_term)

        image_urls = []
        for document_id in ranked_documents:
            document = db.session.get(Document, document_id)
            soup = BeautifulSoup(document.body, "html.parser")
            for img in soup.find_all("img"):
                image_urls.append({"url": img["src"], "document_id": document.id})

        return image_urls


engine = Engine()
