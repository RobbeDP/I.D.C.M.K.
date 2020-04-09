from configparser import ConfigParser
from imgurpython import ImgurClient

config = ConfigParser()
config.read('./idcmk.ini')

CLIENT_ID = config['imgur']['client_id']
CLIENT_SECRET = config['imgur']['client_secret']
client = ImgurClient(CLIENT_ID, CLIENT_SECRET)

def image_fetch(query):
    pass
