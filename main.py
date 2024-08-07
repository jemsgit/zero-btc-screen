import json
import random
import time
import threading
import multiprocessing
import atexit
import socket
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import qrcode
from PIL import Image
import RPi.GPIO as GPIO

from config.builder import Builder
from config.config import config
from config.currency_config import currencyConfig
from logs import logger
from presentation.observer import Observable

from alarm.alarm_manager import alarmManager as alarmManager
from settings_server.server import initSettingsServer
from settings_server.server_web import app

web_server_port = 5001

BUTTON_CURRENCY_CHANNEL = 4 #GPIO 4
BUTTON_INTERVAL_CHANNEL = 16 #GPIO 16

API_INTERVALS = ['m', 'h', 'd', 'w', 'M']

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_CURRENCY_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_INTERVAL_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=%sUSDT'
API_URL_CANDLE = 'https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1%s&limit=21'

currencyList = currencyConfig.currencyList or ['BTC']
currency_index = 0
currency_interval_index = 1
server_process = None

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def create_IP_QRCODE():
    ip_address = get_ip_address()
    url = f'http://{ip_address}:{web_server_port}'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    desired_size = (100, 100)
    img = img.resize(desired_size, Image.ANTIALIAS)
    img.save("qr_code.png")

def start_web_server():
    global server_process
    server_process = multiprocessing.Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': web_server_port})
    server_process.start()

def stop_web_server(process):
    global server_process
    if server_process and server_process.is_alive():
        server_process.terminate()
        server_process.join()
        print("Flask server stopped.")
    else:
        print("Flask server is not running.")

atexit.register(stop_web_server)

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
        print("long button")         
        longCb(event)
        return
    print("short button")         
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

    try:
        start_web_server()
    except:
        print('web server error')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)
    currency = get_currency()
    interval = get_period()

    GPIO.add_event_detect(BUTTON_CURRENCY_CHANNEL, GPIO.RISING, callback=switch_currency, bouncetime=400)
    GPIO.add_event_detect(BUTTON_INTERVAL_CHANNEL, GPIO.RISING, callback=switch_interval, bouncetime=400)

    create_IP_QRCODE()
    data_sink.showQR()

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
        stop_web_server()
        exit()


if __name__ == "__main__":
    main()
