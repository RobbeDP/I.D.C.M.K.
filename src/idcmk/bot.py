import logging
import json
import random

from configparser import ConfigParser
from .image_fetch import ImgurFetcher
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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

with open('idcmk/json/question(re)marks.json') as file2:
    remarks = json.load(file2)

# Initialize blacklisted users set
black_list = {

}


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.chat.send_message('Opbokken kut, zoek het zelf maar uit.')


def show_image_url(update, context):
    message = update.message
    if hasattr(message, 'text'):
        if message.from_user.username not in black_list:
            # message sometimes doesn't have text
            text = message.text.lower().strip()
            query = searches.get(text, None)  # gets None if nothing was found

            if query is not None:
                link = IMGUR_FETCHER.fetch(query)
                message.chat.send_message(link)

                return True

    return False


def answer_question(update, context):
    message = update.message
    if message.from_user.username not in black_list:
        text = message.text.lower().strip().split(" ")
        if text.endswith("?"):
            for word in remarks:
                if word in text:
                    possible_remarks = remarks[word]
                    message.reply_text(possible_remarks[random.randint(0, len(possible_remarks) - 1)])
                    return True

    return False


def text_handler(update, context):
    if show_image_url(update, context):
        return
    elif answer_question(update, context):
        return


def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def run():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config['telegram']['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
