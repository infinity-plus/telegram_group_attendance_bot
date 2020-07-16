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

    def initialize(self):
        updater = Updater(token=self.TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Enable logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
        logger = logging.getLogger(__name__)

        def error(update, context):
            logger.warning('Update "%s" caused error "%s"', update,
                           context.error)

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)
        start_attendance_handler = CommandHandler('start_attendance',
                                                  self.start_attendance)
        mark_attendance_handler = CallbackQueryHandler(self.mark_attendance)
        end_attendance_handler = CommandHandler('end_attendance',
                                                self.end_attendance)
        dispatcher.add_handler(start_attendance_handler)
        dispatcher.add_handler(mark_attendance_handler)
        dispatcher.add_handler(end_attendance_handler)

        # log all errors
        dispatcher.add_error_handler(error)
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
        if (update.effective_chat.type != update.effective_chat.GROUP
            ) and (update.effective_chat.type !=
                   update.effective_chat.SUPERGROUP):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="This command can only be used in groups!")
            return
        original_member = context.bot.get_chat_member(update.effective_chat.id,
                                                      update.effective_user.id)
        if original_member['status'] in ('creator', 'administrator'):
            if ('flag' in context.chat_data) and (context.chat_data['flag']
                                                  == 1):
                update.message.reply_text(
                    "Please close the current attendance first")
                return
            elif ('flag'
                  not in context.chat_data) or (context.chat_data['flag']
                                                == 0):
                context.chat_data['flag'] = 1
                context.chat_data['list'] = []
                context.chat_data['id'] = update.effective_chat.id
                keyboard = [[
                    InlineKeyboardButton("Present", callback_data='present')
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                self.message = update.message.reply_text(
                    "Please mark your attendance", reply_markup=reply_markup)
        else:
            # update.message.reply_text("Only admins can execute this command")
            pass

    @run_async
    def mark_attendance(self, update, context):
        query = update.callback_query
        choice = query.data
        if (choice == 'present') and ('@' + update.effective_user.username
                                      not in context.chat_data['list']):
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

    def end_attendance(self, update, context):
        if (update.effective_chat.type != update.effective_chat.GROUP
            ) and (update.effective_chat.type !=
                   update.effective_chat.SUPERGROUP):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="This command can only be used in groups!")
            return
        original_member = context.bot.get_chat_member(update.effective_chat.id,
                                                      update.effective_user.id)
        if original_member['status'] in ('creator', 'administrator'):
            if (context.chat_data['id'] != update.effective_chat.id):
                return
            str1 = ("\n".join(context.chat_data['list']))
            context.bot.edit_message_text(
                text=
                "Attendance is over. {} people(s) marked attendance. Here is the list: \n {}"
                .format(len(context.chat_data['list']), str1),
                chat_id=self.message.chat_id,
                message_id=self.message.message_id)
            context.chat_data['flag'] = 0
            context.chat_data['list'] = []
        else:
            # update.message.reply_text("Only admins can execute this command")
            pass


def main():
    attendance_checker = attendance_bot(Config)
    attendance_checker.initialize()


if __name__ == '__main__':

    main()
