import numpy as np
from collections import Counter
import re
import json
import logging
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

class DocumentIndexer:
    def __init__(self):
        self.docs_path = Path(__file__).parent.parent / 'data' / 'docs'
        self.doc_contents = {}
        self.vocab = {}
        self.idf = None
        self.doc_vectors = {}

        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

        # Initialize stop words
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize the indexer
        self.initialize()

    def initialize(self):
        """Initialize the indexer by loading and processing documents."""
        try:
            self.docs_path.mkdir(parents=True, exist_ok=True)
            self._load_documents()
            self._build_vocab()
            self._calculate_idf()
            self._vectorize_documents()
        except Exception as e:
            logger.error(f"Error initializing indexer: {str(e)}")
            raise

    def _preprocess_text(self, text):
        """Preprocess text by tokenizing, removing stopwords, and converting to lowercase."""
        # Convert to lowercase and tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        tokens = [token for token in tokens if token not in self.stop_words and token.isalnum()]
        
        return tokens

    def _build_vocab(self):
        """Build vocabulary from all documents."""
        vocab = set()
        for cdp in self.doc_contents:
            for section in self.doc_contents[cdp]['sections']:
                tokens = self._preprocess_text(section['content'])
                vocab.update(tokens)
        
        self.vocab = {word: idx for idx, word in enumerate(sorted(vocab))}

    def _calculate_tf(self, tokens):
        """Calculate term frequency for a document."""
        counter = Counter(tokens)
        tf = np.zeros(len(self.vocab))
        for word, count in counter.items():
            if word in self.vocab:
                tf[self.vocab[word]] = count
        return tf

    def _calculate_idf(self):
        """Calculate inverse document frequency for all terms."""
        n_docs = sum(len(self.doc_contents[cdp]['sections']) for cdp in self.doc_contents)
        doc_freq = np.zeros(len(self.vocab))
        
        for cdp in self.doc_contents:
            for section in self.doc_contents[cdp]['sections']:
                tokens = set(self._preprocess_text(section['content']))
                for token in tokens:
                    if token in self.vocab:
                        doc_freq[self.vocab[token]] += 1
        
        self.idf = np.log(n_docs / (doc_freq + 1)) + 1

    def _vectorize_documents(self):
        """Create TF-IDF vectors for all documents."""
        for cdp in self.doc_contents:
            vectors = []
            for section in self.doc_contents[cdp]['sections']:
                tokens = self._preprocess_text(section['content'])
                tf = self._calculate_tf(tokens)
                tfidf = tf * self.idf
                # Normalize the vector
                norm = np.linalg.norm(tfidf)
                if norm > 0:
                    tfidf = tfidf / norm
                vectors.append(tfidf)
            self.doc_vectors[cdp] = np.array(vectors)

    def _load_documents(self):
        """Load documents from the data directory."""
        for cdp in ['segment', 'mparticle', 'lytics', 'zeotap']:
            doc_path = self.docs_path / f"{cdp}_docs.json"
            
            # If document doesn't exist, create empty placeholder
            if not doc_path.exists():
                self._create_empty_doc(doc_path, cdp)
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    self.doc_contents[cdp] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading documents for {cdp}: {str(e)}")
                continue

    def _create_empty_doc(self, path, cdp):
        """Create an empty document structure for a CDP."""
        empty_doc = {
            "platform": cdp,
            "sections": [
                {
                    "title": "Getting Started",
                    "content": f"Welcome to {cdp.capitalize()} documentation."
                }
            ]
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(empty_doc, f, indent=2)

    def update_documents(self, cdp, documents):
        """Update the documents for a specific CDP."""
        try:
            # Update document contents
            doc_path = self.docs_path / f"{cdp}_docs.json"
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "platform": cdp,
                    "sections": documents
                }, f, indent=2)

            # Reload and reindex all documents
            self.initialize()
            
            logger.info(f"Successfully updated documents for {cdp}")
        except Exception as e:
            logger.error(f"Error updating documents for {cdp}: {str(e)}")
            raise

    def search(self, query, cdp, top_k=3):
        """Search for relevant document sections for a given query and CDP."""
        try:
            if cdp not in self.doc_vectors or not self.doc_vectors[cdp].size:
                logger.warning(f"No documents found for CDP: {cdp}")
                return []

            # Preprocess and vectorize query
            query_tokens = self._preprocess_text(query)
            query_tf = self._calculate_tf(query_tokens)
            query_vector = query_tf * self.idf
            
            # Normalize query vector
            query_norm = np.linalg.norm(query_vector)
            if query_norm > 0:
                query_vector = query_vector / query_norm

            # Calculate cosine similarities
            similarities = np.dot(self.doc_vectors[cdp], query_vector)
            
            # Get top k results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Filter out low similarity results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    section = self.doc_contents[cdp]['sections'][idx]
                    results.append(section['content'])
            
            return results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def get_document_count(self, cdp):
        """Get the number of indexed documents for a CDP."""
        if cdp in self.doc_vectors:
            return len(self.doc_vectors[cdp])
        return 0
