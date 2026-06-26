from HTMLdownloader import Htmldownloader
from URLfrontier import URLfrontier
from ContentParser import ContentParser

class Crawler:
    def __init__(self, start_url = 'https://digiato.com'):
        self.frontier = URLfrontier()
        self.parser = ContentParser()
        self.downloader = Htmldownloader()
        self.graph = {}

        self.frontier.add_url(start_url)

    def crawl_next(self):
        url = self.frontier.get_next()
        if not url:
            return None

        print(f"crawling: {url}")

        html, final_url = self.downloader.downloader(url)
        if not html:
            return None

        if self.parser.is_duplicate(html):
            return None

        links = self.parser.extract_links(html, final_url)
        self.graph.setdefault(url, [])

        for link in links:
            self.graph.setdefault(link, [])

            if link not in self.graph[url]:
                self.graph[url].append(link)

        for link in links:
            self.frontier.add_url(link)

        return self.parser.page_content(html, url)

    def crawl(self, max_pages = 10):
        results = []
        while len(results) < max_pages and self.frontier.has_urls():
            page = self.crawl_next()
            if page:
                results.append(page)
        return results

