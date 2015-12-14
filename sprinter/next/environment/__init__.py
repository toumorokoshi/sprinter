from ..exceptions import SprinterException

EXAMPLE_CONFIG = {
    "ssh": {
        "formula": "sprinter.formula.command"
    }
}


class EnvironmentException(SprinterException):
    pass


class Environment(object):

    def __init__(self, config):
        validate(config)
        pass

    def install(self):
        pass

    def update(self):
        pass

    def remove(self):
        pass

    def to_dict(self):
        pass

    @staticmethod
    def from_dict(config):
        return Environment(config)

    @staticmethod
    def validate(config):
        errors = []
        for name, formula_config in config.items():
            pass
