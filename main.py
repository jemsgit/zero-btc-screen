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
BUTTON_INTERVAL_CHANNEL = 17

API_INTERVALS = ['m', 'h', 'd', 'w', 'M']

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_CURRENCY_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_INTERVAL_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=%sUSDT'
API_URL_CANDLE = 'https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1%s&limit=21'

currencyList = currencyConfig.currencyList or ['BTC']
currency_index = 0
currency_interval_index = 1

def data_mapper_to_old(item):
  data = item[0:5]
  return [float(i) for i in data]

def updateCurrencyList():
  global currencyList
  global currency_index
  currentCurrency = currencyList[currency_index]
  currencyList = currencyConfig.currencyList
  currency_index = currencyList.index(currentCurrency) if currentCurrency in currencyList else -1

currencyConfig.subscribeToUpdates(updateCurrencyList)

def get_dummy_data():
    logger.info('Generating dummy data')

def applyButtonCallback(channel, shortCb, longCb, event):
    start_time = time.time()
    while GPIO.input(channel) == 1: # Wait for the button up
        pass
    buttonTime = time.time() - start_time    # How long was the button down?
    if buttonTime >= 1:         
        longCb(event)
        return
    if buttonTime >= .1:
        shortCb(event)

def switch_currency(event):
  if(stopAlarm()):
      return
  applyButtonCallback(BUTTON_CURRENCY_CHANNEL, switch_currency_forward, switch_currency_back, event)

def switch_currency_forward(event):
    global currency_index
    currency_index +=1
    if(currency_index >= len(currencyList)):
        currency_index = 0

def switch_currency_back(event):
    global currency_index
    currency_index -=1
    if(currency_index < 0):
        currency_index = len(currencyList) - 1

def switch_interval(event):
  if(stopAlarm()):
      return
  applyButtonCallback(BUTTON_INTERVAL_CHANNEL, switch_interval_forward, switch_interval_back, event)

def switch_interval_forward(event):
    global currency_interval_index
    currency_interval_index +=1
    if(currency_interval_index >= len(API_INTERVALS)):
        currency_interval_index = 0

def switch_interval_back(event):
    global currency_interval_index
    currency_interval_index -=1
    if(currency_interval_index < 0):
        currency_interval_index = len(API_INTERVALS) - 1

def stopAlarm():
  if(alarmManager.isAlarm == True):
    alarmManager.stopAlarm()
    return True
  else:
    return False

def get_currency():
    return currencyList[currency_index]

def get_period():
    return API_INTERVALS[currency_interval_index]

def fetch_currency_data(currency, interval):
  prices = None
  current_price = None
  try:
      CURRENCY_API_URL = API_URL % currency
      logger.info('Fetching prices')
      req = Request(CURRENCY_API_URL)
      data = urlopen(req).read()
      external_data = json.loads(data)
      current_price = float(external_data['price'])
      CURRENCY_API_URL = API_URL_CANDLE % (currency, interval)
      logger.info('Fetching prices2')
      req = Request(CURRENCY_API_URL)
      data = urlopen(req).read()
      external_data = json.loads(data)
      prices = map(data_mapper_to_old, external_data)
      prices = [entry[1:] for entry in prices]
  except:
      print('currency error')
      switch_currency_forward(None)
  return (prices, current_price)

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

    GPIO.add_event_detect(BUTTON_CURRENCY_CHANNEL, GPIO.RISING, callback=switch_currency, bouncetime=200)
    GPIO.add_event_detect(BUTTON_INTERVAL_CHANNEL, GPIO.RISING, callback=switch_interval, bouncetime=200)
    
    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices[0], prices[1], currency)
                time_left = config.refresh_interval
                new_currency = currency
                new_interval = interval
                while time_left > 0 and currency == new_currency and interval == new_interval:
                    time.sleep(0.5)
                    time_left -= 0.5
                    new_currency = get_currency()
                    new_interval = get_period()
                    print('check')
                    alarmManager.checkAlarms(currency, prices[1], alarm_callback)
                if(currency != new_currency or interval != new_interval):
                    data_sink.update_observers(None, None, new_currency)
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
