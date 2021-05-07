import configparser
import os

__all__ = ('currencyConfig', 'CurrencyConfig')


class CurrencyConfig:
    def __init__(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'currency-config.cfg')):
        self._conf = self._load_currencies(file_name)

    @property
    def currencyList(self):
        return self._conf.get('Base', 'curencyList')

    def reloadConfig(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'currency-config.cfg')):
        self._conf = self._load_currencies(file_name)

    @staticmethod
    def _load_currencies(file_name):
        conf = configparser.ConfigParser()
        conf.read_file(open(file_name))
        return conf


# we want to import the config across the files
currencyConfig = CurrencyConfig()
