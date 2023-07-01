class CommandBase:
    def __init__(self):
        self.dispatcher = dict(
            on=Commands.command_switch,
            off=Commands.change_lang
        )

    def dispatch(self, command: str, *args, **kwargs):
        return self.dispatcher[command](args, kwargs)


class Commands:
    @staticmethod
    def command_switch(mode, *args, **kwargs):
        pass

    @staticmethod
    def change_lang(lang, *args, **kwargs):
        pass
