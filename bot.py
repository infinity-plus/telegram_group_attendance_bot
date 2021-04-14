#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, run_async, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
import logging

import os
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class attendance_bot:
    def __init__(self, config):
        self.TOKEN = config.bot_api

    def initialize(self):
        updater = Updater(token=self.TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)
        start_attendance_handler = CommandHandler('start_attendance',
                                                  self.start_attendance,
                                                  Filters.group)
        attendance_handler = CallbackQueryHandler(self.attendance)
        dispatcher.add_handler(start_attendance_handler)
        dispatcher.add_handler(attendance_handler)

        # log all errors
        dispatcher.add_error_handler(self.error)
        updater.start_webhook(listen="0.0.0.0",
                              port=int(PORT),
                              url_path=self.TOKEN)
        updater.bot.setWebhook(
            'https://telegram-group-attendance-bot.herokuapp.com/' +
            self.TOKEN)
        updater.idle()

    @run_async
    def start(self, update, context):
        update.message.reply_text("Welcome")

    def start_attendance(self, update, context):
        original_member = context.bot.get_chat_member(update.effective_chat.id,
                                                      update.effective_user.id)
        if original_member['status'] in ('creator', 'administrator'):
            if ('flag' in context.chat_data) and (context.chat_data['flag'] == 1):
                update.message.reply_text(
                    "Please close the current attendance first")
                return
            elif ('flag' not in context.chat_data) or (context.chat_data['flag'] == 0):
                context.chat_data['flag'] = 1
                context.chat_data['list'] = list()
                context.chat_data['id'] = update.effective_chat.id
                keyboard = [
                    [InlineKeyboardButton("Present",
                                          callback_data='present')],
                    [InlineKeyboardButton("End Attendance (Admin only)",
                                          callback_data='end_attendance')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                self.message = update.message.reply_text(
                    "Please mark your attendance", reply_markup=reply_markup)
        else:
            # update.message.reply_text("Only admins can execute this command")
            pass

    @run_async
    def attendance(self, update, context):
        query = update.callback_query
        choice = query.data
        if (choice == 'present'):
            if ('@' + update.effective_user.username not in
                    context.chat_data['list']):
                context.chat_data['list'].append('@' +
                                                 update.effective_user.username)
                context.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text="Your attendance has been marked",
                    show_alert=True)
            else:
                context.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text="Your attendance is already marked",
                    show_alert=True)
        elif choice == 'end_attendance':
            original_member = context.bot.get_chat_member(
                update.effective_chat.id,
                update.effective_user.id)
            if original_member['status'] in ('creator', 'administrator'):
                if (context.chat_data['id'] != update.effective_chat.id):
                    return
                query.answer()
                str1 = str()
                for i in context.chat_data['list']:
                    str1 += i + '\n'
                context.bot.edit_message_text(
                    text="Attendance is over. " +
                    str(len(context.chat_data['list'])) +
                    " marked attendance.\n" +
                    "Here is the list:\n" + str1,
                    chat_id=self.message.chat_id,
                    message_id=self.message.message_id)
                context.chat_data['flag'] = 0
                context.chat_data['list'] = []
            else:
                context.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text="This command can be executed by admin only",
                    show_alert=True)

    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update,
                       context.error)


def main():
    attendance_checker = attendance_bot(Config)
    attendance_checker.initialize()


if __name__ == '__main__':

    main()
