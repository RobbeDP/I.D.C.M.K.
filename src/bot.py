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

# Read in Telegram Bot Token
BOT_TOKEN = config['telegram']['token']

# Initialize responses dictionary. This dictionary maps messages to the corresponding
# queries that will be used to fetch images.
with open('json/search.json') as file:
    searches = json.load(file)

# Initialize blacklisted users set
black_list = {

}

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Opbokken kut, zoek het zelf maar uit.')


def show_image_url(update, context):
    message = update.message
    if hasattr(message, 'text') and message.from_user.username not in black_list:
        # message sometimes doesn't have text
        text = message.text.lower()

        if text == "same":
            message.chat.send_message("same")
        else:
            query = searches.get(text, None)  # gets None if nothing was found

            if query is not None:
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
    dp.add_handler(MessageHandler(Filters.text, show_image_url))

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
