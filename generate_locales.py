#!venv/bin/python
from db import Db


def gen_locales():
    locale = {
        'bot_status': {
            'ru': 'Сейчас бот ',
            'en': 'Currently bot is '
        },
        'enabled': {
            'ru': 'ВКЛЮЧЕН',
            'en': 'ENABLED'
        },
        'disabled': {
            'ru': 'ОТКЛЮЧЕН',
            'en': 'DISABLED'
        },
        'toggle_on': {
            'ru': 'Включить',
            'en': 'Toggle ON'
        },
        'toggle_off': {
            'ru': 'Отключить',
            'en': 'Toggle OFF'
        },
        'lang': {
            'ru': 'Язык: Русский',
            'en': 'Language: English'
        }
    }
    for text_meta, langpack in locale.items():
        for lang, text in langpack.items():
            Db.update_locale(text_meta=text_meta, lang=lang, text=text)


if __name__ == '__main__':
    gen_locales()
