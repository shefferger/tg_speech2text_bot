#!venv/bin/python
import os
import uuid
from telebot import async_telebot, types
import asyncio
from caching import Cache
import db
import signal
from fs import memoryfs
import speech2text


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
            status = self.db.get_status(cid)
            is_enabled = status['is_enabled']
            if not status['lang']:
                lang = 'ru' if msg.from_user.language_code == 'ru' else 'en'
                self.db.set_status(chat_id=cid, is_enabled=is_enabled, lang=lang)
            else:
                lang = status['lang']
            reply = self.db.get_locale('bot_status', lang) + \
                self.db.get_locale('enabled' if is_enabled else 'disabled', lang)
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(str(
                self.db.get_locale('toggle_off' if is_enabled else 'toggle_on', lang)),
                callback_data='bot_' + ('off' if is_enabled else 'on'), row_width=1))
            kb.add(types.InlineKeyboardButton(str(self.db.get_locale('lang', lang)),
                                              callback_data='bot_' + ('ru' if lang == 'ru' else 'en'), row_width=1))

            await self.bot.send_message(chat_id=cid, text=reply, reply_markup=kb, parse_mode='HTML')

        @self.bot.message_handler(func=lambda msg: hasattr(msg, 'reply_to_message') and
                                  hasattr(msg.reply_to_message, 'content_type') and
                                  msg.reply_to_message.content_type == 'voice')
        async def voice_message_handler(msg):
            cid = msg.chat.id
            uid = msg.reply_to_message.from_user.id
            status = self.db.get_status(cid)
            is_enabled = status['is_enabled']
            if not is_enabled:
                return
            if not status['lang']:
                lang = 'ru' if msg.from_user.language_code == 'ru' else 'en'
                self.db.set_status(chat_id=cid, is_enabled=is_enabled, lang=lang)
            else:
                lang = status['lang']
            voice = msg.reply_to_message.voice
            voice_file_id = voice.file_id
            filename = str(uuid.uuid4())
            filename_ogg = f'{filename}.ogg'
            file_info = await self.bot.get_file(voice_file_id)
            downloaded_file = await self.bot.download_file(file_info.file_path)
            with memoryfs.MemoryFS() as memfs:
                filename_wav = speech2text.convert_ogg2wav(filename_ogg, memfs, downloaded_file)
                text = speech2text.transcribe(filename=filename_wav, filesystem=memfs, lang=lang)
            await self.bot.send_message(chat_id=cid, text=text)

        @self.bot.callback_query_handler(func=lambda call: call.data[:3] == 'bot')
        async def callback_handler(call):
            await self.bot.answer_callback_query(callback_query_id=call.id)
            cid = call.message.chat.id
            mid = call.message.message_id
            status = self.db.get_status(cid)
            is_enabled = status['is_enabled']
            if not status['lang']:
                lang = 'ru' if call.from_user.language_code == 'ru' else 'en'
            else:
                lang = status['lang']
            command = call.data[4:]
            text = None
            kb = types.InlineKeyboardMarkup()
            if command == 'on':
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('toggle_off', lang)),
                    callback_data='bot_off', row_width=1))
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('lang', lang)),
                    callback_data='bot_' + lang, row_width=1))
                text = self.db.get_locale('bot_status', lang) + \
                    self.db.get_locale('enabled', lang)
                self.db.set_status(chat_id=cid, is_enabled=True, lang=lang)
            elif command == 'off':
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('toggle_on', lang)),
                    callback_data='bot_on', row_width=1))
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('lang', lang)),
                    callback_data='bot_' + lang, row_width=1))
                text = self.db.get_locale('bot_status', lang) + \
                    self.db.get_locale('disabled', lang)
                self.db.set_status(chat_id=cid, is_enabled=False, lang=lang)
            elif command in ('en', 'ru'):
                lang = 'en' if lang == 'ru' else 'ru'
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('toggle_off' if is_enabled else 'toggle_on', lang)),
                    callback_data='bot_on', row_width=1))
                kb.add(types.InlineKeyboardButton(str(
                    self.db.get_locale('lang', lang)),
                    callback_data='bot_' + ('en' if lang == 'ru' else 'ru'), row_width=1))
                text = self.db.get_locale('bot_status', lang) + \
                    self.db.get_locale('enabled' if is_enabled else 'disabled', lang)
                self.db.set_status(chat_id=cid, is_enabled=is_enabled, lang=lang)
            await self.bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=kb)

    @staticmethod
    def exit_handler(signum, frame):
        for task in asyncio.tasks.all_tasks():
            task.cancel()


if __name__ == '__main__':
    app = App()
