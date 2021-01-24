import logging
import json
import random

from configparser import ConfigParser
from .image_fetch import ImgurFetcher
from telegram.ext import Updater, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# Read in config file
config = ConfigParser()
config.read('../idcmk.ini')

# Initialize imgur fetcher
CLIENT_ID = config['imgur']['client_id']
CLIENT_SECRET = config['imgur']['client_secret']
IMGUR_FETCHER = ImgurFetcher(CLIENT_ID, CLIENT_SECRET)

# Initialize responses dictionary. This dictionary maps messages to the corresponding
# queries that will be used to fetch images.
with open('idcmk/json/search.json') as file:
    searches = json.load(file)

with open('idcmk/json/question(re)marks.json') as file:
    remarks = json.load(file)

# Initialize blacklisted users set
black_list = {}


def answer_text(update, context):
    message = update.message
    if hasattr(message, "text") and message.from_user.username not in black_list:
        # message sometimes doesn't have text
        text = message.text.lower().strip()

        if text == "same":
            message.chat.send_message("same")


def answer_image_url(update, context):
    message = update.message
    if hasattr(message, "text") and message.from_user.username not in black_list:
        # message sometimes doesn't have text
        text = message.text.lower().strip()
        
        if text == "piemel":
            message.chat.send_message("Dag Lucas, je bent een luie kloot, maak uw eigen versie van de bot!!!!!! X De CTO van IDCMK")
            message.chat.send_message("https://i.imgur.com/VLvGPDz.jpg")
        else:
            queries = searches.get(text, None)  # gets None if nothing was found
            if queries is not None:
                query = random.choice(queries)
                link = IMGUR_FETCHER.fetch(query)
                message.chat.send_message(link)

# def answer_question(update, context):
#     message = update.message
#     if message.from_user.username not in black_list:
#         text = message.text.lower().strip().split(" ")
#         if text.endswith("?"):
#             for word in remarks:
#                 if word in text:
#                     possible_remarks = remarks[word]
#                     message.reply_text(possible_remarks[random.randint(0, len(possible_remarks) - 1)])
#                     return True
#
#     return False


def text_handler(update, context):
    answer_text(update, context)
    answer_image_url(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def run():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config['telegram']['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on message
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
