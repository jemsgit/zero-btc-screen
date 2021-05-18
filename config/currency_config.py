import configparser
import os
import threading
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = ('currencyConfig', 'CurrencyConfig')

def getCurrencyList():
  try:
    req = Request(currencyConfig.currencyUrl or 'https://api.github.com/events')
    data = urlopen(req).read()
    external_data = json.loads(data)
    currencyConfig.updateCurrencyList(['BTC,ETH'])
  except (HTTPError, URLError) as e:
    print('Error')


class CurrencyConfig:
    def __init__(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'currency-config.cfg')):
        self._conf = self._load_currencies(file_name)

    @property
    def currencyList(self):
        return self._conf.get('base', 'currencyList').split(',')
    
    @property
    def currencyUrl(self):
        return self._conf.get('currency-update-url', 'url')

    def reloadConfig(self, file_name=os.path.join(os.path.dirname(__file__), os.pardir, 'currency-config.cfg')):
        self._conf = self._load_currencies(file_name)

    def subscribeToUpdates(self, callback):
        self.updateCallback = callback
        x = threading.Thread(target=getCurrencyList)
        x.start()

    @staticmethod
    def _load_currencies(file_name):
        conf = configparser.ConfigParser()
        conf.read_file(open(file_name))
        return conf
    
    def save_config(self):
        with open(os.path.join(os.path.dirname(__file__), os.pardir, 'currency-config.cfg'), 'w') as configfile:
            self._conf.write(configfile)

    def updateCurrencyUrl(self, url):
        self._conf.set('currency-update-url', 'url', url)
        self.save_config()
        self.reloadConfig()

    def updateCurrencyList(self, currencies):
        joiner = ','
        self._conf.set('base', 'currencyList', '%s' % joiner.join(currencies))
        self.save_config()
        self.reloadConfig()
        self.updateCallback()

# we want to import the config across the files
currencyConfig = CurrencyConfig()
