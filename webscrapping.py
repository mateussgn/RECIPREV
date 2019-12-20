import pandas as pd
import requests
from bs4 import BeautifulSoup
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import csv

'''
O scraping foi feito em um site que fornece dados sobre a performance da NBA
Daí já pude montar um gráfico com os dados coletados
'''

'''
Esta função faz o scraping das várias páginas em sequencia
Aproveitando que apenas muda a parte do ano na string url
Então a cada ano é feito a coleta de dados em uma página diferente
Ao final uma unica tabela e retornada com as informações dos anos requisitados
'''
def scrape_stats(base_url, year_start, year_end):
    years = range(year_start, year_end+1, 1)

    final_df = pd.DataFrame()

    for year in years:
        print('Extraindo ano {}'.format(year))
        req_url = base_url.format(year)
        req = requests.get(req_url)
        soup = BeautifulSoup(req.content, 'html.parser')
        table = soup.find('table', {'id':'totals_stats'})
        df = pd.read_html(str(table))[0]
        df['Year'] = year
        final_df = final_df.append(df)

    return final_df

url = 'https://www.basketball-reference.com/leagues/NBA_{}_totals.html'
df = scrape_stats(url, 2013, 2018)

#limpando dados repetidos(table heads repetidos)
drop_indexes = df[df['Rk'] == 'Rk'].index # Pega indexes onde a coluna 'Rk' possui valor 'Rk'
df.drop(drop_indexes, inplace=True) # elimina os valores dos index passados da tabela

# passando dados do tipo objeto para numérico
numeric_cols = df.columns.drop(['Player', 'Pos', 'Tm'])
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
print('Converteu tabelas em numéricos!\n============================')

print('\nTabela dos maiores pontuadores de sexta 3 pontos em cinco temporadas\n============================')
sorted_df = df.sort_values(by=['3P'], axis=0, ascending=False)
print(sorted_df[['Player', '3P', 'Year']].head(n=5))

print('\nTabela ordenada pelo numero de sextas de 3 pontos\n============================')
grouped_df = df.groupby('Player', as_index=False).sum() #agrupa pelo nome do jogador, no caso irá somar todos os seus dados das 5 temporadas
sorted_df = grouped_df.sort_values(by=['3P'], axis=0, ascending=True) #ordena pelo numero de cestas de 3P
print(sorted_df[['Player', '3P', '3PA']].head(n=5))

#Salvando os 10 primeiros cestinhas no arquivo cestinhas.csv 
print('\nEscrevendo no arquivo saida.csv')
sorted_df = sorted_df[['Player', '3P']].tail(n=11)
sorted_df.to_csv('cestinhas.csv', index=False, encoding='utf-8')

#Montagem do gráfico
x = []
y = []

cestinhas = open('cestinhas.csv', 'r') #abre o arquio somente para leitura
for line in cestinhas:
    line = line.strip()
    X, Y = line.split(',')
    x.append(X)
    y.append(Y)

del x[0] #eliminando nome da coluna
del y[0] #eliminando nome da coluna

cestinhas.close()
plt.plot(x, y)
plt.title('Cestinhas')
plt.xlabel('Jogadores')
plt.ylabel('Cestas de 3 pontos')

plt.show()