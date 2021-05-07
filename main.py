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

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

API_URL = 'https://production.api.coindesk.com/v2/price/values/%s?ohlc=true'

currencyList = ['BTC']

CURRENT_CURRENCY_INDEX = 0

def get_dummy_data():
    logger.info('Generating dummy data')

def toggle_timer():
    timer = threading.Timer(1000, switch_currency)
    timer.start()   

def switch_currency():
    CURRENT_CURRENCY +=1
    if(CURRENT_CURRENCY >= len(currencyList)):
        CURRENT_CURRENCY = 0



def fetch_prices():
    CURRENT_CURRENCY = currencyList[CURRENT_CURRENCY_INDEX]
    CURRENCY_API_URL=API_URL % CURRENT_CURRENCY
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
    currencyList = currencyConfig.currencyList
    print(currencyList)

    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices)
                time.sleep(config.refresh_interval)
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
