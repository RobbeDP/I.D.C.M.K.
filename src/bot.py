import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from image_fetch import ImgurFetcher, GoogleFetcher
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

# Initialise google fetcher
API_KEY = config['google']['api_key']
PROJECT_ID = config['google']['project_id']
print(API_KEY)
print(PROJECT_ID)
GOOGLE_FETCHER = GoogleFetcher(API_KEY, PROJECT_ID)

# Read in Telegram Bot Token
BOT_TOKEN = config['telegram']['token']

# Initialize responses dictionary. This dictionary maps messages to the corresponding
# queries that will be used to fetch images.
MSG_TO_QUERY = {
    'trui': 'hoodie',
    'hentai': 'hentai',
    'iets grappigs': 'funny'
}

# Intitialize blacklisted user set
BLACKLISTED = {
    'ManuDeBuck'
}

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Trui xd')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('opbokken kut zoek het zelf maar uit')


def trui(update, context):
    message = update.message
    if hasattr(message, 'text') and message.from_user.username not in BLACKLISTED:
        # sometimes doesn't have text lol
        text = message.text.lower()
        query = MSG_TO_QUERY.get(text, None)  # gets None if nothing was found

        if query is not None:
            link = GOOGLE_FETCHER.fetch(query)
            print(link)
            message.chat.send_message(link)

def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
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
