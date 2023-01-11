import requests
import config
class FMP_api:
    def __init__(self,api,symbol):
        self.BASE_URL = 'https://financialmodelingprep.com/api'
        self.api = api
        self.symbol = symbol
    def get_profile(self):
        url = f"{self.BASE_URL}/v3/profile/{self.symbol}?apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_bs(self):
        url = f"{self.BASE_URL}/v3/balance-sheet-statement/{self.symbol}/?period=quarter&apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_news(self):
        url = f"{self.BASE_URL}/v3/stock_news?tickers={self.symbol}&limit=50&apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_shares(self):
        url = f"{self.BASE_URL}/v4/shares_float?symbol={self.symbol}&apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_is(self):
        url = f"{self.BASE_URL}/v3/income-statement/{self.symbol}/?period=quarter&apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_cf_qtr(self):
        url = f"{self.BASE_URL}/v3/cash-flow-statement/{self.symbol}/?period=quarter&apikey={self.api}"
        r = requests.get(url)
        return r.json()
    def get_quote(self):
        url = f"{self.BASE_URL}/v3/quote-short/{self.symbol}/?period=quarter&apikey={self.api}"
        r = requests.get(url)
        return r.json()

class poly_api:
    def __init__(self,api,symbol):
        self.BASE_URL = 'https://financialmodelingprep.com/api'
        self.api = api
        self.symbol = symbol