import os
import ujson

class Config:

    # loads a configuration from the specified file,
    # and initializes an instance of Config
    def __init__(self, config_filename):
        self.filename = config_filename
        self.values = self.load_config(config_filename)

    # returns a value of the specified parameter if the parameter exists
    # otherwise, returns an empty string
    def get(self, name):
        if name in self.values:
            return self.values[name]
        return ''

    # updates the specified parameter
    def set(self, name, value):
        self.values[name] = value

        # loads a configration from the specified file
    def load_config(self, config_filename):
        if not config_filename in os.listdir():
            print('cannot find ' + config_filename)
            return {}
        with open(config_filename) as f:
            return ujson.load(f)

    # loads a private RSA key from a json file
    def load_key(self, filename):
        if not filename in os.listdir():
            print('cannot find ' + filename)
            return
        with open(filename) as f:
            return PrivateKey.load_pkcs1(f.read())