import pandas as pd
import pandas_market_calendars as mcal
import numpy as np
import streamlit as st
import datetime as dt
nyse = mcal.get_calendar('NYSE')


def price_stats(df):
    # df['ticker'] = df
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df['t'] = df['t'].dt.tz_localize('UTC')
    df['t'] = df['t'].dt.tz_convert('America/New_York')

    #df['D2 Date'] = df['t'] + pd.tseries.offsets.CustomBusinessDay(1, holidays=nyse.holidays().holidays)
    #df['D2 Date'] = pd.to_datetime(df['D2 Date']).dt.strftime("%m-%d-%Y")
    df['t'] = pd.to_datetime(df['t']).dt.strftime("%m-%d-%Y")


    df['Gap Up%'] = df['o'] / df['c'].shift(1) - 1
    df['HOD%'] = df['h'] / df['o'] - 1
    df['Close vs Open%'] = df['c'] / df['o'] - 1
    df['Low vs Open%'] = df['l']/df['o']-1
    df['Close%'] = df['c'] / df['c'].shift(1) - 1
    df['Gap Up?'] = np.where((df['Gap Up%'] > 0), 1, 0)
    df['v'] = df['v'] / 1000000
    df['$ Vol'] = df['vw'] * df['v']
    df['Close Below Open?'] = np.where((df['Close vs Open%'] < 0), 1, 0)

    df['PMH'] = 0
    #df['D2 Open'] = df['o'].shift(-1)
    #df['D2 High'] = df['h'].shift(-1)
    #df['D2 Low'] = df['l'].shift(-1)
    #df['D2 Close'] = df['c'].shift(-1)
    #df['D2 vwap'] = df['vw'].shift(-1)
    #df['D2 Vol'] = df['v'].shift(-1)
    #df['D2 $Vol'] = df['D2 Vol'] * df['D2 vwap']
    #df['D2 Run%'] = df['c'].shift(-1) / df['c'] - 1
    #df['D2 CvH%'] = df['c'].shift(-1) / df['h'].shift(-1) - 1
    #df['D2 CvO%'] = df['c'].shift(-1) / df['o'].shift(-1) - 1
    df.dropna(inplace=True)