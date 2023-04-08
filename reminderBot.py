import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Replace this with your bot token
TOKEN = r"6279267795:AAGzgkFWxpNTaYgxFseAppkDDp_VBbtd8yE"

# Reminder list
reminder_list = []

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! I'm your group reminder bot. Type /add or /remove to manage the reminder list.")

def add_item(update: Update, context: CallbackContext):
    item = ' '.join(context.args)
    if item:
        reminder_list.append(item)
        update.message.reply_text(f"Added '{item}' to the reminder list.")
    else:
        update.message.reply_text("Usage: /add <item>")

def remove_item(update: Update, context: CallbackContext):
    item = ' '.join(context.args)
    if item in reminder_list:
        reminder_list.remove(item)
        update.message.reply_text(f"Removed '{item}' from the reminder list.")
    else:
        update.message.reply_text("Item not found in the reminder list. Usage: /remove <item>")

def list_items(update: Update, context: CallbackContext):
    if reminder_list:
        response = "Reminder List:\n"
        for item in reminder_list:
            response += f"- {item}\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text("The reminder list is empty. Use /add to add items.")

def main():
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_item))
    dispatcher.add_handler(CommandHandler("remove", remove_item))
    dispatcher.add_handler(CommandHandler("list", list_items))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
