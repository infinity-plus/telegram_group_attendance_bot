#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, run_async, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
import logging

import os
PORT = int(os.environ.get('PORT', 5000))

class attendance_bot:
    def __init__(self, config):
        self.TOKEN = config.bot_api
        self.flag = 0
        self.user_list = []

    def initialize(self):
        updater = Updater(token=self.TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)
        start_attendance_handler = CommandHandler('start_attendance', self.start_attendance)
        mark_attendance_handler= CallbackQueryHandler(self.mark_attendance)
        end_attendance_handler = CommandHandler('end_attendance', self.end_attendance)
        dispatcher.add_handler(start_attendance_handler)
        dispatcher.add_handler(mark_attendance_handler)
        dispatcher.add_handler(end_attendance_handler)
        updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=self.TOKEN)
        updater.bot.setWebhook('https://telegram-group-attendance-bot.herokuapp.com/' + self.TOKEN)

    @run_async
    def start(self, update, context):
        update.message.reply_text("Welcome")

    def start_attendance(self, update, context):
        self.flag += 1
        if self.flag != 1:
            update.message.reply_text("Please close the current attendance first")
            return
        original_member = context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        if original_member['status'] in ('creator', 'administrator'):
            keyboard = [[InlineKeyboardButton("Present", callback_data='present')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.message = update.message.reply_text("Please mark your attendance", reply_markup=reply_markup)
        else:
            update.message.reply_text("Only admins can execute this command")

    @run_async
    def mark_attendance(self, update, context):
        query = update.callback_query
        choice = query.data
        if (choice == 'present') and ('@'+update.effective_user.username not in self.user_list):
            self.user_list.append('@'+update.effective_user.username)
            context.bot.answer_callback_query(callback_query_id=query.id, text="Your attendance has been marked", show_alert=True)
        else:
            context.bot.answer_callback_query(callback_query_id=query.id, text="Your attendance is already marked", show_alert=True)

    def end_attendance(self, update, context):
        original_member = context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        if original_member['status'] in ('creator', 'administrator'):
            str1=("\n".join(self.user_list))
            context.bot.edit_message_text(text="Attendance is over. {} people(s) marked attendance. Here is the list: \n {}".format(len(self.user_list),
                                            str1), chat_id=self.message.chat_id, message_id=self.message.message_id)
        self.flag = 0
        self.user_list=[]
def main():
    attendance_checker = attendance_bot(Config)
    attendance_checker.initialize()

if __name__ == '__main__':

    main()
