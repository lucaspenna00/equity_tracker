from equity_research.equity_research import EquityResearch
from datetime import date

ticker=input("Digite o Ticker desejado: ")
ano=int(input("Digite o ano: "))
mes=int(input("Digite o mes: "))
dia=int(input("Digite o dia: "))

eqr = EquityResearch()
eqr.get_DRE(ticker, date(ano,mes,dia))
