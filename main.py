import json
import random
import time
import threading
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.builder import Builder
from config.config import config
from config.currency_config import currencyConfig
from logs import logger
from presentation.observer import Observable

from alarm.alarm_manager import alarmManager as alarmManager
from settings_server.server import initSettingsServer

import RPi.GPIO as GPIO

BUTTON_CURRENCY_CHANNEL = 4
BUTTON_INTERVAL_CHANNEL = 5

API_INTERVALS = ['s', 'm', 'h', 'd', 'M', 'Y']

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_CURRENCY_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_INTERVAL_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=%sUSDT'
API_URL_CANDLE = 'https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1%s&limit=20'

currencyList = currencyConfig.currencyList or ['BTC']
currency_index = 0
currency_interval_index = 3

def data_mapper_to_old(item):
  return item[0:5]

def updateCurrencyList():
  global currencyList
  global currency_index
  currentCurrency = currencyList[currency_index]
  currencyList = currencyConfig.currencyList
  currency_index = currencyList.index(currentCurrency) if currentCurrency in currencyList else -1

currencyConfig.subscribeToUpdates(updateCurrencyList)

def get_dummy_data():
    logger.info('Generating dummy data') 

def switch_currency(event):
    stopAlarm()
    global currency_index
    currency_index +=1
    if(currency_index >= len(currencyList)):
        currency_index = 0

def switch_currency_back(event):
    stopAlarm()
    global currency_index
    currency_index -=1
    if(currency_index < 0):
        currency_index = len(currencyList) - 1

def switch_interval(event):
    stopAlarm()
    global currency_interval_index
    currency_interval_index +=1
    if(currency_interval_index >= len(API_INTERVALS)):
        currency_interval_index = 0

def switch_interval_back(event):
    stopAlarm()
    global currency_interval_index
    currency_interval_index -=1
    if(currency_interval_index < 0):
        currency_interval_index = len(API_INTERVALS) - 1

def stopAlarm():
  if(alarmManager.isAlarm == True):
    alarmManager.stopAlarm()

def get_currency():
    return currencyList[currency_index]

def get_period():
    return API_INTERVALS[currency_interval_index]

def fetch_currency_data(currency, interval):
    CURRENCY_API_URL = API_URL % currency
    logger.info('Fetching prices')
    req = Request(CURRENCY_API_URL)
    data = urlopen(req).read()
    external_data = json.loads(data)
    current_price = external_data['price']
    CURRENCY_API_URL = API_URL_CANDLE % currency, interval
    logger.info('Fetching prices2')
    req = Request(CURRENCY_API_URL)
    data = urlopen(req).read()
    external_data = json.loads(data)
    prices = map(data_mapper_to_old, external_data)
    prices = [entry[1:] for entry in prices]
    return {prices: prices, current_price: current_price }

def fetch_prices():
    currency = get_currency()
    interval = get_period()
    return fetch_currency_data(currency, interval)

def alarm_callback(cur):
    print("alarm")


def main():
    logger.info('Initialize')
    try:
        initSettingsServer()
    except:
        print('bluetooth error')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)
    currency = get_currency()
    interval = get_period()

    GPIO.add_event_detect(BUTTON_CURRENCY_CHANNEL, GPIO.RISING, callback=switch_currency, bouncetime=400)
    GPIO.add_event_detect(BUTTON_CURRENCY_CHANNEL, GPIO.RISING, callback=switch_currency_back, bouncetime=1500)
    GPIO.add_event_detect(BUTTON_INTERVAL_CHANNEL, GPIO.RISING, callback=switch_interval, bouncetime=400)
    GPIO.add_event_detect(BUTTON_INTERVAL_CHANNEL, GPIO.RISING, callback=switch_interval_back, bouncetime=1500)
    
    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices.prices, prices.current_price, currency)
                time_left = config.refresh_interval
                new_currency = currency
                new_interval = interval
                while time_left > 0 and currency == new_currency and interval == new_interval:
                    time.sleep(0.5)
                    time_left -= 0.5
                    new_currency = get_currency()
                    new_interval = get_period()
                    alarmManager.checkAlarms(currency, fetch_prices, alarm_callback)
                if(currency != new_currency or interval != new_interval):
                    data_sink.update_observers(None, new_currency)
                currency = new_currency
                interval = new_interval
            except (HTTPError, URLError) as e:
                logger.error(str(e))
                time.sleep(5)
    except IOError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info('Exit')
        data_sink.close()
        exit()


if __name__ == "__main__":
    main()
