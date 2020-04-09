from imgurpython import ImgurClient
import random


class HoodieFetcher:

    def __init__(self, client_id, client_secret):
        self.client = ImgurClient(client_id, client_secret)


    def fetch(self):
        # do request to get albums
        albums = self.client.gallery_search('hoodie')

        # if got at least one album, pick a random one and return link of first image
        if len(albums) > 0:
            album = random.choice(albums)
            if hasattr(album, 'images'):
                # sometimes there are no images...
                return album.images[0]['link']

