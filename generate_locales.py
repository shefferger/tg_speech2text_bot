#!venv/bin/python
from db import Db


def gen_locales():
    locale = {
        'bot_status': {
            'ru': 'Сейчас бот',
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
        }
    }
    # TO DO: добавить инсерт/апдейт в базу


if __name__ == '__main__':
    gen_locales()
