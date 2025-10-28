import requests
from parsel import Selector
from fake_useragent import FakeUserAgent

class PageFetcher:
    """
    Class responsible to fetch data from a given URL.
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": FakeUserAgent().random
        })

    def get_html(self, url: str) -> str:
        """
        Fetch and return html from the given URL.
        """
        response = self.session.get(url)
        response.encoding = 'utf-8'
        return response.text

    def get_selector(self, url: str) -> Selector:
        """
        Create a Selector object from the given URL.
        """
        html = self.get_html(url)
        return Selector(html)
