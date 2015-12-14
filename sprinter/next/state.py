from .exceptions import SprinterException

EXAMPLE = """
packages:
  sprinter:
    updated_date: 2015-12-10T02:59:43Z
    user_input: {}
    config: {}

""".strip()


class StateException(SprinterException):
    pass


class SprinterState(object):

    def __init__(self, config):
        self._validate(config)

    @staticmethod
    def load(path):
        pass

    @staticmethod
    def save(path, config):
        pass
