import pandas as pd
import simfin as sf
from simfin.names import *
import yahooquery as yf
from datetime import date, datetime
from tqdm import tqdm
import logging
from pathlib import Path
import inspect
import pickle

class EquityResearchUS():
    def __init__(self, prices_file=None, financial_statements_file=None, name_to_save_DB="equities_database"):
        sf.set_data_dir('data/us')
        sf.set_api_key(api_key='free')
        p = Path("log")
        p.mkdir(exist_ok=True)
        logging.basicConfig( filename="log/equity_research_us.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')
        self.prices_file = prices_file
        self.financial_statements_file = financial_statements_file
        self.name_to_save_DB = name_to_save_DB

    def _load_DB_prices(self, stock_list):
        func_name = inspect.currentframe().f_code.co_name

        if self.prices_file != None:
            print("[INFO] Loading Yahoo Prices data...")
            file = open(f"data/us/{self.prices_file}.pickle",'rb')
            df_prices = pickle.load(file)
            file.close()
        else:
            print("[INFO] Downloading Yahoo Prices data...")
            tickers = yf.Ticker(stock_list)
            df_prices = tickers.history(period='max')

        df_prices_fin = pd.DataFrame()
        print("[INFO] Buillding Yahoo DB prices...")
        for ticker in stock_list:
            try:
                df_prices_aux = df_prices[ticker]
                df_prices_aux['security'] = ticker
                df_prices_fin = df_prices_fin.append(df_prices_aux)
            except:
                error_msg = f"[{func_name}] Daily prices database for {ticker} not found. May be deslisted."
                logging.error(error_msg)
                pass
        return df_prices_fin


    def _build_us_equities_db(self):
        print("[INFO] Loading financial statements...")

        df_income = sf.load(dataset='income', variant='quarterly', market='us')
        df_income = df_income.reset_index()
        
        df_balance = sf.load_balance(variant='quarterly', market='us')
        df_balance = df_balance.reset_index()

        df_cashflow = sf.load_cashflow(variant='quarterly', market='us')
        df_cashflow = df_cashflow.reset_index()

        print("[INFO] Loading stock prices...")

        stock_list = df_income['Ticker'].unique().tolist()

        df_prices_fin = self._load_DB_prices(stock_list)

        df_prices_fin = df_prices_fin.reset_index().rename({"index":"Publish Date", "security":"Ticker", 'adjclose':'price'}, axis=1)
        df_prices_fin = df_prices_fin[['Publish Date', 'Ticker','price']]

        df_income.drop(['SimFinId', 'Currency', 'Restated Date'], axis=1, inplace=True)
        df_balance.drop(['SimFinId', 'Currency', 'Restated Date'], axis=1, inplace=True)
        df_cashflow.drop(['SimFinId', 'Currency', 'Restated Date'], axis=1, inplace=True)

        df_income['Report Date'] = df_income['Report Date'].astype(str)
        df_income['Publish Date'] = df_income['Publish Date'].astype(str)

        df_balance['Report Date'] = df_balance['Report Date'].astype(str)
        df_balance['Publish Date'] = df_balance['Publish Date'].astype(str)

        df_cashflow['Report Date'] = df_cashflow['Report Date'].astype(str)
        df_cashflow['Publish Date'] = df_cashflow['Publish Date'].astype(str)

        print("[INFO] Merging Income, Balance and Cash Flow...")

        db_equities = pd.DataFrame()
        db_equities = df_income.merge(df_balance, how='left', on=['Ticker', 'Report Date', 'Fiscal Year', 'Fiscal Period', 'Publish Date'])
        db_equities = db_equities.merge(df_cashflow, how='left', on=['Ticker', 'Report Date', 'Fiscal Year', 'Fiscal Period', 'Publish Date'])
        
        db_equities['Publish Date'] = pd.to_datetime(db_equities['Publish Date'])
        df_prices_fin['Publish Date'] = pd.to_datetime(df_prices_fin['Publish Date'])

        print("[INFO] Merging ASOF stock prices and financial statements...")
        db_equities_with_prices = pd.merge_asof(db_equities.sort_values("Publish Date"), df_prices_fin.sort_values("Publish Date"), by=['Ticker'], on=['Publish Date'], allow_exact_matches=False, direction='forward')

        print("[INFO] Saving DB equities...")
        db_equities_with_prices.to_csv(f"data/us/{self.name_to_save_DB}", index=False)

    def get_equities_DB(self):
        if self.financial_statements_file != None:
            df = pd.read_csv(f"data/us/{self.financial_statements_file}")
        else:
            df = self._build_us_equities_db()
        return df


