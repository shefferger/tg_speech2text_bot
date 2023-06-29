#!venv/bin/python
import os
from telebot import async_telebot, types
import asyncio


class App:
    def __init__(self):
        self.bot = async_telebot.AsyncTeleBot(os.getenv('TOKEN'))
        self.register_hanlders()
        asyncio.run(self.bot.polling())

    @staticmethod
    def getlocale(meta_text: str) -> str:
        return ''

    def register_hanlders(self):
        @self.bot.message_handler(commands=['help', 'start', 'status'])
        async def start(message):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('Назад', callback_data='kekw', row_width=1))
            await self.bot.reply_to(message, "Hello!")

        @self.bot.message_handler(func=lambda message: True)
        async def echo_message(message):
            await self.bot.reply_to(message, message.text)


if __name__ == '__main__':
    app = App()
