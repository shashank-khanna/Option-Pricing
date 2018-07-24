import datetime
import logging

import pandas as pd
import quandl
from pandas.tseries.offsets import BDay
from pandas_datareader import data

from config import QUANDL_KEY

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

quandl.ApiConfig.api_key = QUANDL_KEY

SOURCES = ['yahoo', 'morningstar']


def get_ranged_data(ticker, start, end=None, useQuandl=True):
    if not end:
        end = datetime.date.today()
    df = pd.DataFrame()
    if useQuandl:
        logging.info("Fetching data for Ticker=%s from Source=Quandl" % ticker)
        df = quandl.get("WIKI/" + ticker, start_date=start, end_date=end)
        logging.info("### Successfully fetched data!!")
    else:
        for source in SOURCES:
            try:
                logging.info("Fetching data for Ticker=%s from Source=%s" % (ticker, source))
                df = data.DataReader(ticker, source, start, end)
                if not df.empty:
                    logging.info("### Successfully fetched data!!")
                    break
            except Exception as exception:
                logging.warn("Received exception from Source=%s for Ticker=%s" % (source, ticker))
                logging.warn(str(exception))
    return df


def get_data(ticker, useQuandl=True):
    df = pd.DataFrame()
    if useQuandl:
        logging.info("Fetching data for Ticker=%s from Source=Quandl" % ticker)
        df = quandl.get("WIKI/" + ticker)
        logging.info("### Successfully fetched data!!")
    else:
        for source in SOURCES:
            try:
                logging.info("Fetching data for Ticker=%s from Source=%s" % (ticker, source))
                df = data.DataReader(ticker, source)
                if not df.empty:
                    logging.info("### Successfully fetched data!!")
                    break
            except Exception as exception:
                logging.warn("Received exception from Source=%s for Ticker=%s" % (source, ticker))
                logging.warn(str(exception))
    return df


def get_treasury_rate(ticker=None):
    df = pd.DataFrame()
    if not ticker:
        ticker = 'DTB3'  # Default to 3-Month Treasury Rate
    prev_business_date = datetime.datetime.today() - BDay(1)
    logging.info("Fetching data for Ticker=%s from Source=Quandl" % ticker)
    df = quandl.get("FRED/" + ticker, start_date=prev_business_date - BDay(1), end_date=prev_business_date)
    if df.empty:
        logging.error("Unable to get Treasury Rates from Quandl. Please check connection")
        raise IOError("Unable to get Treasury Rate from Quandl")
    logging.info("### Successfully fetched data!!")
    print(df['Value'][0])
    return df['Value'][0]


def get_spx_prices(start_date=None):
    if not start_date:
        start_date = datetime.datetime(2017, 1, 1)
    df = pd.DataFrame()
    df = get_data('SPX', start_date, useQuandl=False)
    if df.empty:
        logging.error("Unable to get SNP 500 Index from Web. Please check connection")
        raise IOError("Unable to get Treasury Rate from Web")
    return df


if __name__ == '__main__':
    # df = get_data('AAPL', datetime.datetime(2017, 1, 1), useQuandl=True)
    # df = get_data('SPX', datetime.datetime(2017, 1, 1), useQuandl=False)
    df = get_data('WMT', useQuandl=True)
    print(df.head())
    print(df.tail())
    # rate = get_treasury_rate()
    # print type(rate), rate
