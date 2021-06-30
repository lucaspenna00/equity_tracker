import yahooquery as yf
import pandas as pd
import numpy as np
from datetime import date
from tqdm import tqdm
import warnings
import inspect
import logging
from pathlib import Path

class BlackLitterman():

    def __init__(self, security_max_confidence: str, date_init: date, date_final: date, df_securities_expected_returns: pd.DataFrame(), epsilon: float, n_iterations: int):
        p = Path("log")
        p.mkdir(exist_ok=True)
        logging.basicConfig( filename="log/black_litterman.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')
        list_of_stocks = df_securities_expected_returns.index.tolist()
        self.n_stocks = len(list_of_stocks)
        self.security_max_confidence = security_max_confidence
        self.K = 252 # fator de anualização
        self.N = n_iterations
        self.epsilon = epsilon
        self.df_expected_returns = df_securities_expected_returns
        self.returns_matrix = self._get_returns_matrix(list_of_stocks)
        self.date_init = date_init
        self.date_final = date_final
        self.iterations_history = pd.DataFrame(columns=list_of_stocks+["constant", "error", "sharpe"])

    def _get_returns_matrix(self, list_of_stocks: list) -> pd.DataFrame():
        df_returns = pd.DataFrame()
        df_returns['date'] = yf.Ticker('PETR4'+".SA").history(period='max').reset_index()['date'].tolist()
        for stock in list_of_stocks:
            stock_data = yf.Ticker(stock+".SA").history(period='max').reset_index()
            stock_data['close_previous'] = stock_data['close'].shift(1)
            stock_data['return_'+stock] = (stock_data['close'] - stock_data['close_previous'])/stock_data['close_previous']
            stock_data = stock_data[['date','return_'+stock]]
            df_returns = pd.merge(df_returns, stock_data, how='left', on='date')
        df_returns = df_returns.dropna()
        df_returns = df_returns[(df_returns['date'] >= self.date_init) & (df_returns['date'] <= self.date_final)]
        df_returns.set_index("date", inplace=True)
        return df_returns

    def _volatility(self, weights: pd.DataFrame()) -> float:
        covmatrix = self.returns_matrix.cov() * self.K
        var = weights.T @ covmatrix @ weights
        vol = np.sqrt(var.values[0][0])
        return vol

    def _get_vol_weight_partial_derivative(self, weights: pd.DataFrame(), index_da_derivada: str) -> float:
        x = weights.copy()
        x_h = weights.copy()
        h=self.epsilon
        x_h.loc[index_da_derivada, "weights"] = x_h['weights'].iloc[index_da_derivada] + h
        return (self._volatility(x_h)-self._volatility(x))/h

    def fit_portfolio(self):

        stocks_aux = self.list_of_stocks.copy()
        stocks_aux.remove(self.security_max_confidence)
        for _i in tqdm(range(0, self.N)):
            
            # generate random weights
            weights = np.array(np.random.random(self.n_stocks))
            weights = weights / np.sum(weights)

            # generate pandas dataframe
            df_weights = pd.DataFrame()
            df_weights['security'] = self.list_of_stocks
            df_weights['weights'] = weights
            df_weights.set_index("security", inplace=True)

            #calculate constant
            return_max_confidence = self.df_expected_returns['expected_returns'].iloc[self.security_max_confidence]
            derivative = self._get_vol_weight_partial_derivative(weights, self.security_max_confidence)
            constant = return_max_confidence/derivative

            for stock in stocks_aux:
                derivative = self._get_vol_weight_partial_derivative(weights, stock)
                implicity_return = constant*derivative

                #salvar implicity return por ativo

            # dataframe self.iterations_history por iteracao: colunas: [weights_ativos], constante, error, sharpe

            # calcular erro absoluto medio entre retornos implicitos e percentuais
            # calcular sharpe
            # redirect results to log

    def get_portfolio(self, criteria: str) -> pd.DataFrame():
        this_function_name = inspect.currentframe().f_code.co_name

        if self.iterations_history.shape[0] <= 0:
            error_msg = f"[{this_function_name} is portfolio fitted? iterations history data not found.s]"
            logging.error(error_msg)
            raise Exception(error_msg)
        else:
            if criteria == "sharpe":
                df_filt = self.iterations_history[self.iterations_history['sharpe'] == self.iterations_history['sharpe'].max()].copy()
            elif criteria == "error":
                df_filt = self.iterations_history[self.iterations_history['error'] == self.iterations_history['error'].min()].copy()
            else:
                error_msg = f"[{this_function_name} criteria not found. Choose between sharpe or error]"
                logging.error(error_msg)
                raise Exception(error_msg)

        return df_filt










