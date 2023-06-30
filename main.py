#!venv/bin/python
import os

import requests
from telebot import async_telebot, types
import asyncio
from caching import Cache
import db
import signal


class App:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_handler)
        self.bot = async_telebot.AsyncTeleBot(os.getenv('TOKEN'))
        self.register_hanlders()
        self.db = db.Db()
        asyncio.run(self.bot.polling())

    @Cache.cache(delta=60)
    def getlocale(self, meta_text: str, lang: str) -> str:
        return self.db.get_locale(text_meta=meta_text, lang=lang)

    def register_hanlders(self):
        @self.bot.message_handler(commands=['help', 'start', 'status'])
        async def start_menu_handler(msg):
            cid = msg.chat.id
            lang = 'ru' if msg.from_user.language_code == 'ru' else 'en'
            is_enabled = self.db.get_status(cid)['is_enabled']
            reply = self.db.get_locale('bot_status', lang) + \
                self.db.get_locale('enabled' if is_enabled else 'disabled', lang)
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(str(
                self.db.get_locale('toggle_off' if is_enabled else 'toggle_on', lang)),
                callback_data='bot_' + ('off' if is_enabled else 'on'), row_width=1))

            await self.bot.send_message(chat_id=cid, text=reply, reply_markup=kb, parse_mode='HTML')

        @self.bot.message_handler(func=lambda msg: True)  # content_types=['voice', 'audio'])
        async def voice_message_handler(msg):
            cid = msg.chat.id
            await self.bot.send_message(chat_id=cid, text='спс')
            # file_info = self.bot.get_file(msg.voice.file_id)
            # file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
            #                     format(os.getenv('TOKEN'), file_info.file_path))
            # src = file_info.file_path[:6] + 'oga' + file_info.file_path[5:]
            # dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
            # await self.bot.reply_to(msg, msg.text)

        @self.bot.callback_query_handler(func=lambda call: call.data[:3] == 'bot')
        async def callback_handler(call):
            await self.bot.answer_callback_query(callback_query_id=call.id)
            cid = call.message.chat.id
            mid = call.message.message_id
            # uid = call.from_user.id
            lang = 'ru' if call.from_user.language_code == 'ru' else 'en'
            command = call.data[4:]
            text = None
            kb = types.InlineKeyboardMarkup()
            if command == 'on':
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('toggle_off', lang)),
                    callback_data='bot_off', row_width=1))
                text = self.db.get_locale('bot_status', lang) + \
                       self.db.get_locale('enabled', lang)
                self.db.set_status(chat_id=cid, is_enabled=True)
            elif command == 'off':
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('toggle_on', lang)),
                    callback_data='bot_on', row_width=1))
                text = self.db.get_locale('bot_status', lang) + \
                       self.db.get_locale('disabled', lang)
                self.db.set_status(chat_id=cid, is_enabled=False)
            await self.bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=kb)

    @staticmethod
    def exit_handler(signum, frame):
        for task in asyncio.tasks.all_tasks():
            task.cancel()


if __name__ == '__main__':
    app = App()
