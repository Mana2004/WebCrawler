from collections import deque

class URLfrontier():
    def __init__(self):
        self.queue = deque()
        self.seen_urls = set()

    def add_url(self, url):
        if url not in self.seen_urls:
            self.queue.append(url)
            self.seen_urls.add(url)

    def get_next(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def has_urls(self):
        return len(self.queue) > 0




