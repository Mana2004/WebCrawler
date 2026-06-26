import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json


class ContentParser:
    def __init__(self):
        self.seen_hashes = set()

    def get_hash(self, html):
        return hashlib.md5(html.encode()).hexdigest()

    def is_duplicate(self, html):
        hash_value = self.get_hash(html)
        if hash_value in self.seen_hashes:
            return True
        self.seen_hashes.add(hash_value)
        return False


    def extract_links(self, html, base_url):
        page = BeautifulSoup(html, 'html.parser')
        links = []

        for link in page.find_all('a'):
            href = link.get("href")
            if not href:
                continue
            abs_url = urljoin(base_url, href)
            abs_url = abs_url.split("#")[0]
            if 'digiato.com' not in abs_url:
                continue
            if '?' in abs_url:
                continue
            if any(abs_url.lower().endswith(ext) for ext in
                   ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.zip', '.doc', '.css', '.js']):
                continue
            path = urlparse(abs_url).path
            if path == '' or path == '/':
                continue

            if any(path.startswith('/' + p + '/') or path == '/' + p for p in
                   ['category', 'tag', 'author', 'page', 'search', 'homepage']):
                continue

            links.append(abs_url)

        return links

    def page_content(self, html, url):
        page = BeautifulSoup(html, 'html.parser')
        title = page.title.string if page.title else ""

        date = ""
        time_tag = page.find('time')
        if time_tag and time_tag.get('datetime'):
            date = time_tag['datetime']
        else:
            meta_date = (
                    page.find('meta', {'property': 'article:published_time'}) or
                    page.find('meta', {'name': 'publish-date'}) or
                    page.find('meta', {'property': 'og:published_time'})
            )
            if meta_date and meta_date.get('content'):
                date = meta_date['content']

        if not date:
            for script in page.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'datePublished' in data:
                            date = data['datePublished']
                            break
                        elif '@graph' in data:
                            for item in data['@graph']:
                                if 'datePublished' in item:
                                    date = item['datePublished']
                                    break
                except Exception:
                    continue

        category = ""
        meta_category = page.find('meta', {'property': 'article:section'})
        if meta_category and meta_category.get('content'):
            category = meta_category['content']
        else:
            cat_elem = page.find('a', class_=re.compile(r'category|cat|section'))
            if cat_elem:
                category = cat_elem.get_text(strip=True)
            else:
                cat_elem = page.find('span', class_=re.compile(r'category|cat|section'))
                if cat_elem:
                    category = cat_elem.get_text(strip=True)


        for noisy_tag in page(['script', 'style', 'header', 'nav', 'footer', 'aside']):
            noisy_tag.decompose()

        article = page.find('article')
        if not article:
            article = page.find('div', class_=re.compile(r'post-content|entry-content|article-body|story-text'))
        if not article:
            article = page.find('main')
        if not article:
            article = page.body

        text = article.get_text().strip() if article else ""
        text = re.sub(r'\n+', '\n', text)

        return{
            'url' : url,
            'title' : title,
            'date' : date,
            'category' : category,
            'text' : text
        }
