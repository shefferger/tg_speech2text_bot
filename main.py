#!venv/bin/python
import os
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
        async def start(msg):
            cid = msg.chat.id
            lang = 'ru' if msg.from_user.language_code == 'ru' else 'en'
            is_enabled = self.db.get_status(cid)
            reply = self.db.get_locale('bot_status', lang) + \
                self.db.get_locale('enabled' if is_enabled else 'disabled', lang)
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(
                self.db.get_locale('disable' if is_enabled else 'enable', lang),
                callback_data='bot_' + ('off' if is_enabled else 'on'), row_width=1))

            await self.bot.send_message(chat_id=cid, text=reply, reply_markup=kb, parse_mode='HTML')

        @self.bot.message_handler(func=lambda message: True)
        async def echo_message(msg):
            await self.bot.reply_to(msg, msg.text)

        @self.bot.callback_query_handler(func=lambda call: call.data[:3] == 'bot')
        async def callback_handler(call):
            await self.bot.answer_callback_query(callback_query_id=call.id)
            cid = call.message.chat.id
            mid = call.message.message_id
            uid = call.from_user.id

    @staticmethod
    def exit_handler(signum, frame):
        for task in asyncio.tasks.all_tasks():
            task.cancel()


if __name__ == '__main__':
    app = App()
