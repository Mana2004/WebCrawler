import json
import os
from Crawler import Crawler
from SearchEngine import SearchEngine


def main():
    cache_file = "crawled_pages.json"

    if os.path.exists(cache_file):
        print("Loading articles from local cache file...")
        with open(cache_file, "r", encoding="utf-8") as f:
            pages = json.load(f)
    else:
        print("Cache file not found. Starting crawler...")
        crawler = Crawler()
        pages = crawler.crawl(100)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(pages, f, ensure_ascii=False, indent=4)

    search_engine = SearchEngine(index_name="articles")
    search_engine.index_documents(pages)

    print("\nSearch Terminal Ready...")
    print("Enter a 1 or 2 word query (or type 'exit' to quit):")

    while True:
        query = input("\nSearch: ")
        if query.strip().lower() == 'exit':
            break

        results = search_engine.search(query)

        if not results:
            continue

        print(f"\nFound {len(results)} matches:")
        for idx, match in enumerate(results, start=1):
            print(f"\n[{idx}] {match['title']}")
            print(f"URL: {match['url']}")
            print(f"Score: {round(match['jaccard_weight'], 4)}")
            print(f"Snippet: {match['snippet']}")
            print("-" * 40)


if __name__ == "__main__":
    main()