class Command:
    def __init__(self, name, options=None, args=None):
        self.name = name
        self.options = options or []
        self.args = args or []

    def to_string(self):
        return " ".join([self.name] + self.options + self.args)