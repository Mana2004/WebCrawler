import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time

class Htmldownloader:
    def __init__(self, timeout = 5):
        self.timeout = timeout
        self.robots_cache = {}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        self.delay = 0.1

    def robotfile(self, url):
        domain = urlparse(url).netloc

        if domain not in self.robots_cache:
            rf = RobotFileParser()
            rf.set_url(f"https://{domain}/robots.txt")
            try:
                rf.read()
            except Exception:
                pass
            self.robots_cache[domain] = rf

        return self.robots_cache[domain].can_fetch('*',url)

    def downloader(self, url):
        if not self.robotfile(url):
            print(f"blocked by robots.txt: {url}")
            return None, None

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            time.sleep(self.delay)
            return response.text, response.url
        except requests.RequestException as e:
            print(f"download error {url}: {e}")
            return None, None


