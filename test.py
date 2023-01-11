import streamlit as st
import finplot
import requests
import pandas as pd
from api import FMP_api
from stats import price_stats
import config
import datetime
import sqlite3
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib import pyplot as plt
#from market_profile import MarketProfile
import pandas_market_calendars as mcal
df_profit = pd.read_excel("C:\\Users\\yusun\\OneDrive - Huntington Hospitality Financial Corporation\\EDWARDY HHG\\P&L Review\\data_pl.xlsx")

listOfLists = [x for x in df_profit if type(x) == list]

goodType = [int, float]

SUMtest += sum([x for x in df if type(x) in goodType and ~np.isnan(x)])
print(SUMtest)