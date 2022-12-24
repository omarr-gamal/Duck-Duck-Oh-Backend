import json

from bs4 import BeautifulSoup

import nltk
nltk.download('punkt')
nltk.download('stopwords')

from models import Index, Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Engine:
    def __init__(self):
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words=self.stop_words)
        
        self.index = {}
        self.documents = [document.body for document in Document.query.all()]
        
        ind = Index.query.first()
        if not ind:
            ind = Index('{}')
            ind.insert()
            
            self.index_all_documents()
    
        self.index = json.loads(ind.index)
            
        self.vectorizer.fit(self.documents)
        
    def index_all_documents(self):
        for document in Document.query.all():
            tokens = self.__tokenize(document.body)
            self.__add_to_index(document.id, tokens)
    
    def __update_index(self):
        index_json = json.dumps(self.index)
        
        index = Index.query.first()
        index.index = index_json
        
        index.update()
    
    def __tokenize(self, body):
        # split body into tokens
        tokens = nltk.word_tokenize(body)
        
        # remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # stem tokens
        stemmer = nltk.stem.PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def __add_to_index(self, document_id, tokens):
        # add document to index
        for token in tokens:
            if token in self.index:
                self.index[token].append(document_id)
            else:
                self.index[token] = [document_id]
                
        self.__update_index()
    
    def add_document(self, body):
        document = Document(body)
        document.insert()
    
        # add document to list of documents
        self.documents.append(body)
    
        # tokenize and add to index
        tokens = self.__tokenize(body)
        self.__add_to_index(document.id, tokens)
    
        self.vectorizer.fit(self.documents)
           
    def __search_index(self, search_term):
        search_tokens = self.__tokenize(search_term)
        
        # get documents that match search tokens
        matching_documents = []
        for token in search_tokens:
            if token in self.index:
                matching_documents += self.index[token]
        
        # remove duplicates
        matching_documents = list(set(matching_documents))
        
        return matching_documents
    
    def __rank_results(self, documents, search_term):
        # Check if documents list is empty or search_term is empty
        if not len(documents) or not search_term:
            return []

        # Get document bodies
        bodies = [Document.query.get(document_id).body for document_id in documents]

        # Get vectors for search term and documents
        search_vector = self.vectorizer.transform([search_term])
        document_vectors = self.vectorizer.transform(bodies)

        # Calculate cosine similarity between search vector and document vectors
        similarities = [cosine_similarity(search_vector, document_vector)[0][0] for document_vector in document_vectors]

        # Rank documents by similarity
        ranked_documents = [document for _, document in sorted(zip(similarities, documents), reverse=True)]

        return ranked_documents
    
    # return a list of document ids that are ranked based on relevance to search_term
    def search(self, search_term):
        # search index
        documents = self.__search_index(search_term)
        
        # rank documents by relevance
        ranked_documents = self.__rank_results(documents, search_term)
        
        return ranked_documents

    def search_images(self, search_term):
        # Get matching documents
        matching_documents = self.__search_index(search_term)

        # Get image URLs from matching documents
        image_urls = []
        for document_id in matching_documents:
            document = Document.query.get(document_id)
            
            # parse HTML and extract image URLs
            soup = BeautifulSoup(document.body, 'html.parser')
            for img in soup.find_all('img'):
                image_urls.append({
                    'url': img['src'],
                    'document_id': document.id
                })

        return image_urls
