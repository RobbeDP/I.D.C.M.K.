import logging
import json

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from image_fetch import ImgurFetcher, GoogleFetcher, LimitExceededError
from configparser import ConfigParser

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

# Initialize google fetcher
API_KEY = config['google']['api_key']
PROJECT_KEY = config['google']['project_key']
GOOGLE_FETCHER = GoogleFetcher(API_KEY, PROJECT_KEY)

# Read in Telegram Bot Token
BOT_TOKEN = config['telegram']['token']

# Initialize responses dictionary. This dictionary maps messages to the corresponding
# queries that will be used to fetch images.
with open('json/search.json') as file:
    searches = json.load(file)

# Intitialize blacklisted user set
with open('json/blacklist.json') as file:
    black_list = json.load(file)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('opbokken kut zoek het zelf maar uit')


def trui(update, context):
    message = update.message
    if hasattr(message, 'text') and message.from_user.username not in black_list:
        # message sometimes doesn't have text
        text = message.text.lower()
        query = searches.get(text, None)  # gets None if nothing was found

        if query is not None:
            # If google limit is exceed, switch to imgur
            try:
                link = GOOGLE_FETCHER.fetch(query)
            except LimitExceededError:
                link = IMGUR_FETCHER.fetch(query)

            message.chat.send_message(link)


def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, trui))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
