import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Updater, CommandHandler,
                          CallbackContext, CallbackQueryHandler)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Replace this with your bot token
TOKEN = "6279267795:AAETkHzj0COEQPgRrMtQWme0vbCN9qfumIg"

# Reminder list
reminder_list = []

# Group chat ID
group_chat_id = None


def start(update: Update, context: CallbackContext):
    global group_chat_id
    group_chat_id = update.message.chat_id
    update.message.reply_text(
        "Hi! I'm your group reminder bot. Type /add or /remove to manage the reminder list.")


def add_item(update: Update, context: CallbackContext):
    item = ' '.join(context.args)
    if item:
        reminder_list.append(item)
        update.message.reply_text(f"Added '{item}' to the reminder list.")
    else:
        update.message.reply_text("Usage: /add <item>")


def remove_item(update: Update, context: CallbackContext):
    if reminder_list:
        keyboard = []

        for item in reminder_list:
            keyboard.append([InlineKeyboardButton(
                item, callback_data=f"remove:{item}")])

        # Add a "Close" button
        keyboard.append([InlineKeyboardButton("Close", callback_data="close")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Select an item to remove or close the UI:", reply_markup=reply_markup)
    else:
        update.message.reply_text(
            "The reminder list is empty. Use /add to add items.")


def send_reminder(context: CallbackContext):
    job = context.job
    chat_id = job.context

    if reminder_list:
        response = "Reminder List:\n"
        for item in reminder_list:
            response += f"- {item}\n"
    else:
        response = "The reminder list is empty. Use /add to add items."

    context.bot.send_message(chat_id=chat_id, text=response)


def set_interval(update: Update, context: CallbackContext):
    try:
        interval = int(context.args[0]) * 60  # Convert minutes to seconds

        if 'reminder_job' in context.chat_data:
            context.chat_data['reminder_job'].schedule_removal()

        chat_id = update.message.chat_id
        new_job = context.job_queue.run_repeating(
            send_reminder, interval=interval, first=0, context=chat_id)
        context.chat_data['reminder_job'] = new_job

        update.message.reply_text(
            f"Reminder interval set to {context.args[0]} minutes.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /setinterval <minutes>")


def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/add <item> - Add an item to the reminder list\n"
        "/remove - Remove an item from the reminder list by selecting it\n"
        "/list - List all items in the reminder list\n"
        "/setinterval <minutes> - Set the interval for automatic reminders\n"
        "/help - Show this help message\n"
    )
    update.message.reply_text(help_text)


def list_items(update: Update, context: CallbackContext):
    if reminder_list:
        response = "Reminder List:\n"
        for item in reminder_list:
            response += f"- {item}\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text(
            "The reminder list is empty. Use /add to add items.")


def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == 'close':
        query.edit_message_text("UI closed. Use /remove to open it again.")
        return

    action, item = data.split(':', 1)

    if action == 'remove':
        if item in reminder_list:
            reminder_list.remove(item)
            query.answer(f"Removed '{item}' from the reminder list.")

            # Update the inline keyboard
            keyboard = []

            for remaining_item in reminder_list:
                keyboard.append([InlineKeyboardButton(
                    remaining_item, callback_data=f"remove:{remaining_item}")])

            # Add a "Close" button
            keyboard.append([InlineKeyboardButton(
                "Close", callback_data="close")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                "Select an item to remove or close the UI:", reply_markup=reply_markup)
        else:
            query.answer("Item not found in the reminder list.")
    else:
        query.answer("Unknown action.")


def main():
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_item))
    dispatcher.add_handler(CommandHandler("remove", remove_item))
    dispatcher.add_handler(CommandHandler("list", list_items))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler(
        "setinterval", set_interval, pass_args=True, pass_job_queue=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
