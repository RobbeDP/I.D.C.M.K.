import random
import requests
import math
from imgurpython import ImgurClient

class LimitExceededError(Exception):
    pass

class ImgurFetcher:
    def __init__(self, client_id, client_secret):
        self.client = ImgurClient(client_id, client_secret)

    def fetch(self, query):
        # do request to get albums
        albums = self.client.gallery_search(query)

        # if got at least one album, pick a random one and return link of first image
        if len(albums) > 0:
            album = random.choice(albums)
            if hasattr(album, 'images') and len(album.images) > 0:
                # sometimes there are no images...
                return album.images[0]['link']

class GoogleFetcher:
    def __init__(self, api_key, project_key):
        self.api_key = api_key
        self.project_key = project_key

    def fetch(self, query):
        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.project_key}&q={query}&searchType=image"

        response = self.make_request(url)
        queries = response['queries']['request']
        if len(queries) != 0:
            count = int(queries[0]['count'])
            pages = math.ceil(int(queries[0]['totalResults']) / count)
            start = random.randrange(pages) * count + 1

            #TODO only 32 bit integers allowed here

            if start != 1:
                response = self.make_request(url)

            results = response['items']

            if len(results) > 0:
                result = random.choice(results)
                if 'link' in result:
                    return result['link']

    @staticmethod
    def make_request(url):
        response = requests.get(url).json()

        if response['error']['code'] == 403:
            raise LimitExceededError()

        return response
