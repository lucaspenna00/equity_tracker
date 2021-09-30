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
import numpy as np
import time

class EquityResearchUS():
    def __init__(self, prices_file=None, financial_statements_file=None, name_to_save_DB="equities_database.csv"):
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
            df_prices_fin = pd.read_csv(f"data/us/{self.prices_file}")
            return df_prices_fin

        else:
            print("[INFO] Downloading Yahoo Prices data...")
            list_df=[]
            for ticker in tqdm(stock_list):
                try:
                    df_prices = yf.Ticker(ticker).history(period='max').reset_index()
                    df_prices['price_next_quarter'] = df_prices['adjclose'].shift(-60)
                    list_df.append(df_prices)
                except:
                    error_msg = f"[{func_name}] {ticker} not found. May be deslisted or it doesn't exist."
                    logging.error(error_msg)
                    pass

                time.sleep(np.random.randint(low=2, high=5))

            df_prices_fin = pd.concat(list_df)
            df_prices_fin.to_csv("default_yahoo_prices.csv", index=False)

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

        df_prices_fin = df_prices_fin.rename({"date":"Publish Date", "symbol":"Ticker", 'adjclose':'price'}, axis=1)
        df_prices_fin = df_prices_fin[['Publish Date', 'Ticker','price','price_next_quarter']]

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

        return db_equities_with_prices

    def get_equities_DB(self):
        if self.financial_statements_file != None:
            df = pd.read_csv(f"data/us/{self.financial_statements_file}")
        else:
            df = self._build_us_equities_db()
        return df

    def _get_fiscal_date(self, row): 
        if   row['Fiscal Period'] == 'Q1':
            return date(row['Fiscal Year'], 3, 31)
        elif row['Fiscal Period'] == 'Q2':
            return date(row['Fiscal Year'], 6, 30)
        elif row['Fiscal Period'] == 'Q3':
            return date(row['Fiscal Year'], 9, 30)
        elif row['Fiscal Period'] == 'Q4':
            return date(row['Fiscal Year'], 12, 31)

    def build_feature_engineering(self):

        df = self.get_equities_DB()
        df = df.fillna(0)

        dataset = pd.DataFrame()
        dataset['Ticker'] = df['Ticker']
        dataset['fiscal_date'] = df.apply(self._get_fiscal_date, axis=1)
        dataset['price'] = df['price']
        dataset['price_next_quarter'] = df['price_next_quarter']

        print("[INFO] Calculating primary features...")

        # 1. Patrimonio Liquido / Book Value / Total Equity
        dataset['total_equity'] = df['Total Equity']
        # 2. Dividend Yield
        dataset['dividend_yield'] = df['Dividends Paid'] / (df['Shares (Diluted)_x'] * df['price'])
        # 3. Earning per Shares
        dataset['earning_per_shares'] = df['Net Income'] / df['Shares (Diluted)_x']
        # 4. Net Revenue / Gross Profit
        dataset['gross_profit'] = df['Gross Profit']
        # 5. Price to Earnings Ratio
        dataset['price_to_earnings_ratio'] = df['price'] / ( df['Net Income'] / df['Shares (Diluted)_x'] )
        # 6. Price to Book Ratio
        dataset['price_to_book_ratio'] = df['price'] / df['Total Equity']
        # 7. Price to Sales Ratio
        dataset['price_to_sales_ratio'] = ( df['Shares (Diluted)_x'] * df['price'] ) / df['Revenue']
        # 8. Dividends per Share
        dataset['dividend_per_shares'] = df['Dividends Paid'] / df['Shares (Diluted)_x']
        # 9. Current Ratio
        dataset['current_ratio'] = df['Total Current Assets'] / df['Total Current Liabilities']
        # 10. Quick Ratio
        dataset['quick_ratio'] = ( df['Total Current Assets'] - df['Inventories'] ) / df['Total Current Liabilities']
        # 11. Debt Equity Ratio
        dataset['debt_equity_ratio'] = df['Total Current Liabilities'] / df['Total Equity']
        # 12. Profit Margin
        dataset['profit_margin'] = df['Net Income'] / df['Revenue']
        # 13. Operating Margin
        dataset['operating_margin'] = df['Operating Income (Loss)'] / df['Revenue']
        # 14. Asset Turnover
        dataset['asset_turnover'] = df['Revenue'] / df['Total Assets']
        # 15. Return on Asset
        dataset['return_on_asset'] = df['Net Income'] / df['Total Assets']
        # 16. Return on Equity
        dataset['ROE'] = df['Net Income'] / df['Total Equity']
        # 17. Price to Cash Flow Ratio
        # TODO
        # 18. Cash Ratio
        dataset['CR'] = df['Cash, Cash Equivalents & Short Term Investments'] / df['Total Current Liabilities']
        # 19. Enterprise Multiple
        EV = (df['Shares (Diluted)_x'] * df['price']) + df['Total Liabilities'] - df['Cash, Cash Equivalents & Short Term Investments']
        EBITDA = df['Gross Profit'] + df['Operating Expenses']
        dataset['EM'] = EV/EBITDA
        # 20. Long Term Debt to Total Assets
        dataset['long_term_debt/total_assets'] = df['Long Term Debt'] / df['Total Assets']
        # 21. Working Capital Ratio
        dataset['WCR'] = df['Total Current Assets'] / df['Total Current Liabilities']

        return dataset

    def build_dataset(self):

        dataset = self.build_feature_engineering()

        tickers = dataset['Ticker'].unique().tolist()

        list_df = []

        print("[INFO] Calculating delta features...")

        for ticker in tqdm(tickers):
            df_filt = dataset[dataset['Ticker'] == ticker]
            df_filt = df_filt.sort_values(by='fiscal_date')
            
            _returns = ((df_filt['price_next_quarter'] - df_filt['price'])/(df_filt['price'])).copy()
            _ticker = df_filt['Ticker'].copy()
            _fiscal_date = df_filt['fiscal_date'].copy()
            
            df_filt.drop(['Ticker', 'fiscal_date', 'price', 'price_next_quarter'], axis=1, inplace=True)
            
            df_filt = df_filt.pct_change()
            df_filt = df_filt[1:]
            df_filt = df_filt.fillna(0)
            
            df_filt['return'] = _returns
            df_filt['Ticker'] = _ticker
            df_filt['fiscal_date'] = _fiscal_date
            
            list_df.append(df_filt)

        dataset = pd.concat(list_df)

        dataset = dataset.dropna()

        dataset = dataset.replace(np.inf, 0)
        dataset = dataset.replace(-np.inf, 0)

        return dataset

