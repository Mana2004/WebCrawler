# Web Crawler & Search Engine

A modular Persian information retrieval system consisting of a focused web crawler and a search engine powered by Elasticsearch 8.x and a custom Jaccard similarity re-ranking pipeline.

---

## 1. Crawler Architecture & Data Extraction
The system utilizes a clean, separated architecture to safely fetch and clean web data:
* **`URLfrontier.py`:** Manages the URL queue, prioritizing unvisited links and preventing duplicate crawling.
* **`HTMLdownloader.py`:** Handles network operations, executing HTTP requests and capturing raw HTML safely.
* **`ContentParser.py`:** Leverages BeautifulSoup to extract semantic tags (`<h1>`, `<p>`, date, category) while removing boilerplate layout noise (scripts, CSS, navs).
* **`Crawler.py`:** Coordinates the workflow, fetching URLs from the frontier, passing them to the downloader, and feeding extracted links back to the frontier.

---

## 2. Preprocessing & Indexing Method
To deal with the complexities of the Persian language, texts are normalized before entering **Elasticsearch 8.x**:
* **`PersianPrep.py`:** Uses the Hazm NLP library to normalize letters (e.g., standardizing character spacing and unifying Arabic/Persian glyph variations), tokenize words, remove stop words, and perform stemming/lemmatization.
* **Dual-Field Indexing:** Documents are indexed with both raw fields (`title`, `text`) for user-facing terminal outputs/snippets, and cleaned fields (`processed_title`, `processed_text`) dedicated strictly to exact text matching.

---

## 3. Ranking Algorithm
The engine employs a highly efficient two-stage retrieval and re-ranking approach:

1.  **Phase 1 (Elasticsearch Candidate Retrieval):** Evaluates the user query against the processed fields using a fast boolean match query, yielding up to the top $1000$ most relevant candidate documents.
2.  **Phase 2 (Local Jaccard Re-ranking):** Computes the strict Jaccard Similarity index between the query token set ($Q$) and the document token set ($D$):

$$J(Q, D) = \frac{|Q \cap D|}{|Q \cup D|}$$

3.  **Title Boosting:** To ensure that keyword matches in headings heavily outweigh matches in body text, the title's score is multiplied by $10.0$:

$$\text{Final Score} = (J_{\text{title}} \times 10.0) + J_{\text{text}}$$

The top matches are continuously tracked using a Min-Heap (`heapq`), guaranteeing that only the top $K$ results are returned in descending order.

---

## 4. Sample Queries & Terminal Output
The terminal interface supports one-word and two-word queries:

```text
Search: هوش مصنوعی

Found 2 matches:

[1] یادگیری ماشین و کاربردهای آن در هوش مصنوعی
URL: [https://example.com/ai-article](https://example.com/ai-article)
Score: 10.1425
Snippet: ...بررسی الگوریتم‌های هوش مصنوعی و شبکه‌های عصبی عمیق در صنایع مختلف...
----------------------------------------
