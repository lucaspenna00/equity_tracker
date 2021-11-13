import pandas as pd
import numpy as np
import yahooquery as yf
import matplotlib.pyplot as plt
from datetime import date
from tqdm import tqdm
import plotly.graph_objects as go

class GeneticPortfolio():
    def __init__(self, stock_views: dict, start_date: date, end_date: date, population_size=1000, F=2, CR=0.2, N_iterations=1000, live_plot=False, K=60):
        self.list_of_stocks = list(stock_views.keys())
        self.expected_returns = np.array(list(stock_views.values()))
        self.start_date = start_date
        self.end_date = end_date
        self.return_matrix = self._get_portfolio_returns_matrix()
        self.covariance_matrix = np.array(self.return_matrix.cov()*K)
        self.number_of_gens = len(self.list_of_stocks)
        self.population_size = population_size
        self.F = F
        self.CR = CR
        self.N_iterations = N_iterations
        self.global_best_chromosome = None
        self.live_plot = live_plot

        if self.live_plot:
            self.live_fig = go.FigureWidget()
            self.live_fig.layout.title = 'Fitness Evolution along generations'
            self.live_fig.layout.xaxis.title = "Generation"
            self.live_fig.layout.yaxis.title = "Fitness (Sharpe Ratio)"
        
        # Litterman Factors
        '''
        mkt_weights = pd.read_excel("data/mktcap.xlsx")
        self.market_cap_weights = mkt_weights[self.list_of_stocks]
        self.tau = 1
        self.delta = 1
        self.uncertainty_matrix = np.random.normal(0, 1, (self.number_of_gens, self.number_of_gens))
        self.link_matrix = np.diag(np.full(self.number_of_gens,1))
        self.prior_expected_returns = self.delta*self.covariance_matrix @ self.market_cap_weights
        self.views_vector = np.full(shape=self.number_of_gens, fill_value=0.05, dtype=float)
        '''

    def real_time_plot(self) -> "go.FigureWidget()":
        if self.live_plot:
            self.live_fig.add_scatter()
            return self.live_fig

    def _get_portfolio_returns_matrix(self) -> "pd.DataFrame()": 
        df_returns = pd.read_csv("data/matrix_returns.csv", parse_dates=['date'])
        df_returns['date'] = df_returns['date'].dt.date
        df_returns = df_returns.fillna(0) #gambiarra
        df_returns = df_returns[(df_returns['date'] >= self.start_date) & (df_returns['date'] <= self.end_date)]
        df_returns = df_returns[self.list_of_stocks]
        return df_returns

    def _portfolio_vol(self, chromosome: "np.array()") -> float:
        var = chromosome.T @ self.covariance_matrix @ chromosome
        return np.sqrt(var)

    def _portfolio_expected_return(self, chromosome: "np.array()") -> float:
        '''
        first_part = np.linalg.inv((np.linalg.inv(self.tau*self.covariance_matrix)+(np.transpose(self.link_matrix) @ self.uncertainty_matrix @ self.link_matrix)))
        second_part = (np.linalg.inv(self.tau*self.covariance_matrix)@self.prior_expected_returns) + (np.transpose(self.link_matrix) @ self.uncertainty_matrix @ self.views_vector)
        expected_excess_return_vector = first_part @ second_part
        return expected_excess_return_vector @ chromosome
        '''
        return self.expected_returns @ chromosome

    def _apply_restriction(self, chromosome: "np.array()") -> "np.array()":
        '''
        Restrictions:
        -> All weights must be positives;
        -> Sum of weights must be equal 1.
        '''
        _chromosome = chromosome.copy()
        _chromosome = np.abs(_chromosome)
        _chromosome = _chromosome / np.sum(_chromosome)
        return _chromosome

    def _generate_random_chromosome(self) -> "np.array()":
        w = np.random.random(self.number_of_gens)
        w = self._apply_restriction(w)
        return w

    def _generate_population(self) -> "np.array()":
        population=[]
        for _i in range(0, self.population_size):
            population.append(self._generate_random_chromosome())
        return np.array(population)

    def _recombination(self, chromosome: "np.array()", population: "np.array()") -> "np.array()":
        '''
        Recombining to perform genetic variability among the population.
        '''
        chromosome_1 = population[np.random.randint(0, self.population_size)]   # Choose random chromosome 1 from given population
        chromosome_2 = population[np.random.randint(0, self.population_size)]   # Choose random chromosome 2 from given population
        chromosome_modified = chromosome + self.F*(chromosome_1 - chromosome_2) # Perform linear combination => simulating sexual recombination
        chromosome_modified = self._apply_restriction(chromosome_modified)      
        return chromosome_modified

    def _mutation(self, chromosome: "np.array()", best_chromosome: "np.array()") -> "np.array()":
        _chromosome = chromosome.copy()
        for gene in range(0, self.number_of_gens):
            rand = np.random.uniform(0,1)
            if rand <= self.CR:
                _chromosome[gene] = best_chromosome[0]
        _chromosome = self._apply_restriction(_chromosome)
        return _chromosome

    def _fitness(self, chromosome: "np.array()") -> float:
        portfolio_return = self._portfolio_expected_return(chromosome)
        portfolio_vol = self._portfolio_vol(chromosome)
        return portfolio_return/portfolio_vol

    def _initialize_genetic_algo(self) -> (float):

        old_population = self._generate_population()

        max_fitness = -np.inf
        best_chromosome = None

        for chromosome in old_population:
            fit = self._fitness(chromosome)
            if fit > max_fitness:
                max_fitness = fit
                best_chromosome = chromosome

        return max_fitness, best_chromosome


    def fit(self):
        max_fitness, best_chromosome = self._initialize_genetic_algo()
        max_fitness_array = np.array([])
        max_fitness_array =  np.append(max_fitness_array, max_fitness)
        
        for i in tqdm(range(0, self.N_iterations)):

            intermediate_population = self._generate_population()
            for chromosome in intermediate_population:
                recombined_chromosome = self._recombination(chromosome, intermediate_population)
                mutated_chromosome = self._mutation(recombined_chromosome, best_chromosome)

                fitness_not_mutated = self._fitness(chromosome)
                fitness_mutated = self._fitness(mutated_chromosome)

                if fitness_mutated > fitness_not_mutated:
                    _aux_max_fitness = fitness_mutated
                    _aux_best_chromosome = mutated_chromosome
                else:
                    _aux_max_fitness = fitness_not_mutated
                    _aux_best_chromosome = chromosome

                if _aux_max_fitness > max_fitness:
                    max_fitness = _aux_max_fitness
                    best_chromosome = _aux_best_chromosome
                
            max_fitness_array =  np.append(max_fitness_array, max_fitness)

            if self.live_plot:
                self.live_fig.data[0].y = max_fitness_array[:i]
        
        self.fitness_array = max_fitness_array
        self.global_best_chromosome = best_chromosome


    @property
    def best_portfolio(self) -> dict:
        portfolio = dict(zip(self.list_of_stocks, self.global_best_chromosome))
        return portfolio

    @property
    def covmat_shape(self) -> "np.array()":
        return self.covariance_matrix.shape



                


            

            



        





    




    



