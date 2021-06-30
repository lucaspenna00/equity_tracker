import pandas as pd
from datetime import datetime, date
import logging
from pathlib import Path
import unidecode
import warnings
import inspect

class EquityResearch():

    def __init__(self, ibov=True):
        p = Path("log")
        p.mkdir(exist_ok=True)
        logging.basicConfig( filename="log/equity_research.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')

        if ibov:
            sheet_name="IBOVCNPJ"
        else:
            sheet_name="ALLCNPJ"

        self._from_ticker_to_cnpj = pd.read_excel("input/from_ticker_to_cnpj.xlsx", sheet_name=sheet_name)

    def _transform_string(self, x: str) -> str:
        x = unidecode.unidecode(x)
        x = x.replace(" de "," ").replace(" da "," ").replace(" das ", " ").replace(" dos ", " ").replace(" do ", " ")
        x = x.lower()
        return x

    def _filt_df(self, df, ticker, date_arg, column_based, value_to_filt, func_name, name_value):
        if value_to_filt in df[column_based].tolist():
            df = df[df[column_based] == value_to_filt]
        else:
            error_msg = f"[{func_name}] {name_value} for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)

        df = df[df['VL_CONTA'] != 0.0]
        if df.shape[0] > 0:
            value_to_return = df['VL_CONTA'].iloc[0]
        else:
            value_to_return = 0.0
            warning_msg = f"[{func_name}] {name_value} is 0.0 for {ticker} in {date_arg}."
            logging.warning(warning_msg)
            warnings.warn(warning_msg)
        return value_to_return   

    def get_all_tickers(self) -> list:
        return self._from_ticker_to_cnpj['security'].unique().tolist()

    def get_cnpj_from_ticker(self, ticker: str) -> str:
        cnpj = self._from_ticker_to_cnpj[self._from_ticker_to_cnpj['security'] == ticker]
        if cnpj.shape[0] > 0:
            cnpj = cnpj['CNPJ'].iloc[0]
        else:
            error_msg = f"[get_cnpj_from_ticker] CPNJ for {ticker} not found. Verify the if the ticker passed as an argument is correct."
            logging.error(error_msg)
            raise Exception(error_msg)
        return cnpj        

    def get_DRE(self, ticker: str, date_arg: date, log_enabled=True) -> pd.DataFrame():
        this_function_name = inspect.currentframe().f_code.co_name
        cnpj = self.get_cnpj_from_ticker(ticker)
        try:
            filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_con_{date_arg.year}.csv"
            df = pd.read_csv(filename, encoding='iso-8859-1', sep=';') 
            filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_ind_{date_arg.year}.csv"
            df_ind = pd.read_csv(filename, encoding='iso-8859-1', sep=';')
        except:
            raise Exception(f"[{this_function_name}] Data from year {date_arg.year} not found. Check if you have download the cvm data from {date_arg.year}.")
        df = df.append(df_ind)

        if cnpj in df['CNPJ_CIA'].tolist():
            df = df[df['CNPJ_CIA'] == cnpj]
            df = df[df['DT_REFER'] == str(date_arg)]
            df = df[df['DT_INI_EXERC'] == df['DT_INI_EXERC'].max()]
            if log_enabled:
                df.to_excel("log/"+ticker+"_dre.xlsx")
        else:
            error_msg = f"[{this_function_name}] cnpj for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)
        
        return df

    def get_DMPL(self, ticker, date_arg, log_enabled=True) -> pd.DataFrame():
        pass

    def get_gross_revenue(self, ticker: str, date_arg: date) -> float:
        this_function_name = inspect.currentframe().f_code.co_name
        df = self.get_DRE(ticker, date_arg, log_enabled=False)
        gross_revenue = self._filt_df(df, ticker, date_arg, "CD_CONTA", "3.01", this_function_name, "gross_revenue")
        return gross_revenue   

    def get_resultado_bruto(self, ticker: str, date_arg: date) -> float:
        this_function_name = inspect.currentframe().f_code.co_name
        df = self.get_DRE(ticker, date_arg, log_enabled=False)
        resultado_bruto = self._filt_df(df, ticker, date_arg, "CD_CONTA", "3.03", this_function_name, "resultado_bruto")
        return resultado_bruto

    def get_book_value(self, ticker: str, date_arg: date) -> float:
        this_function_name = inspect.currentframe().f_code.co_name
        cnpj = self.get_cnpj_from_ticker(ticker)
        filename=f"data/trimestral/2020/itr_cia_aberta_BPP_ind_{date_arg.year}.csv"
        df = pd.read_csv(filename, sep=';', encoding='ISO-8859-1')
        df = df[df['CNPJ_CIA'] == cnpj]
        df = df[df['DT_REFER'] == str(date_arg)]
        df = df[df['DT_FIM_EXERC'] == str(df['DT_FIM_EXERC'].max())]
        df = df[df['DS_CONTA'] == 'Patrimônio Líquido']
        if df.shape[0] > 0:
            book_value = df['VL_CONTA'].iloc[0]
        else:
            error_msg = f"[{this_function_name}] book value for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)
        return book_value

    def get_paid_dividends(self, ticker: str, date_arg: date) -> float:
        #TODO
        pass


    

    

    


    
    

