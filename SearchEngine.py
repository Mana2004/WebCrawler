import heapq
from elasticsearch import Elasticsearch
from PersianPrep import PersianPrep


class SearchEngine:
    def __init__(self, index_name="articles", hosts=["http://localhost:9200"]):
        self.index_name = index_name.lower()
        self.es = Elasticsearch(hosts)
        self.preprocessor = PersianPrep()

    def index_documents(self, documents):
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)
            print(f"Created index: {self.index_name}")

        print("Indexing documents...")
        for i, doc in enumerate(documents):
            processed_title = self.preprocessor.clean_text(doc.get('title', ''))
            processed_text = self.preprocessor.clean_text(doc.get('text', ''))

            body = {
                'url': doc.get('url'),
                'title': doc.get('title'),
                'text': doc.get('text'),
                'processed_title': processed_title,
                'processed_text': processed_text,
                'date': doc.get('date'),
                'category': doc.get('category')
            }
            self.es.index(index=self.index_name, id=str(i), document=body)

        print(f"Successfully indexed {len(documents)} ")

    def _calculate_jaccard(self, query_tokens, doc_tokens):
        if not doc_tokens:
            return 0.0
        intersection = query_tokens.intersection(doc_tokens)
        union = query_tokens.union(doc_tokens)
        return len(intersection) / len(union)

    def _get_snippet(self, text, query_tokens, length=150):
        if not text:
            return ""
        text_lower = text.lower()
        for token in query_tokens:
            idx = text_lower.find(token)
            if idx != -1:
                start = max(0, idx - 40)
                end = min(len(text), idx + length)
                return ("..." if start > 0 else "") + text[start:end].replace('\n', ' ') + "..."
        return text[:length].replace('\n', ' ') + "..."

    def search(self, query, k=5):
        cleaned_query = self.preprocessor.clean_text(query)
        query_tokens = set(cleaned_query.split())

        if not query_tokens or len(query_tokens) > 2:
            print("Please enter a valid one-word or two-word search query.")
            return []

        es_query = {
            "bool": {
                "should": [
                    {"match": {"processed_title": cleaned_query}},
                    {"match": {"processed_text": cleaned_query}}
                ]
            }
        }

        try:
            response = self.es.search(index=self.index_name, query=es_query, size=1000)
            hits = response['hits']['hits']
        except Exception as e:
            print(f"Elasticsearch execution error: {e}")
            return []

        heap = []

        for hit in hits:
            doc = hit['_source']

            title_tokens = set(doc.get('processed_title', '').split())
            text_tokens = set(doc.get('processed_text', '').split())

            title_jaccard = self._calculate_jaccard(query_tokens, title_tokens)
            text_jaccard = self._calculate_jaccard(query_tokens, text_tokens)

            final_score = (title_jaccard * 10.0) + text_jaccard

            if final_score > 0:
                result_item = {
                    "title": doc.get('title', ''),
                    "url": doc.get('url', ''),
                    "jaccard_weight": final_score,
                    "snippet": self._get_snippet(doc.get('text', ''), query_tokens)
                }

                if len(heap) < k:
                    heapq.heappush(heap, (final_score, doc.get('url'), result_item))
                else:
                    if final_score > heap[0][0]:
                        heapq.heappushpop(heap, (final_score, doc.get('url'), result_item))

        top_k_results = []
        while heap:
            _, _, item = heapq.heappop(heap)
            top_k_results.append(item)

        return top_k_results[::-1]