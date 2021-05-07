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
#from alarm import alarm
from logs import logger
from presentation.observer import Observable

import RPi.GPIO as GPIO

BUTTON_CHANNEL = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

API_URL = 'https://production.api.coindesk.com/v2/price/values/%s?ohlc=true'

currencyList = currencyConfig.currencyList or ['BTC']
currency_index = 0

def get_dummy_data():
    logger.info('Generating dummy data') 

def switch_currency(event):
    global currency_index
    currency_index +=1
    if(currency_index >= len(currencyList)):
        currency_index = 0

def get_currency():
    return currencyList[currency_index]

def fetch_prices():
    currency = get_currency()
    CURRENCY_API_URL = API_URL % currency
    logger.info('Fetching prices')
    timeslot_end = datetime.now(timezone.utc)
    end_date = timeslot_end.strftime(DATETIME_FORMAT)
    start_data = (timeslot_end - timedelta(days=DATA_SLICE_DAYS)).strftime(DATETIME_FORMAT)
    url = f'{CURRENCY_API_URL}&start_date={start_data}&end_date={end_date}'
    req = Request(url)
    data = urlopen(req).read()
    external_data = json.loads(data)
    prices = [entry[1:] for entry in external_data['data']['entries']]
    return prices


def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)
    currency = get_currency()

    GPIO.add_event_detect(BUTTON_CHANNEL, GPIO.RISING, callback=switch_currency, bouncetime=400)

    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices, currency)
                time_left = config.refresh_interval
                new_currency = currency
                while time_left > 0 and currency == get_currency():
                    time.sleep(1)
                    time_left -= 1
                currency = get_currency()
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
