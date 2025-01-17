import pandas as pd

# Carregar o arquivo CSV
file_path = 'datacollection/csv/bins/Bin_1.csv'
df = pd.read_csv(file_path)

# Calcular o preço médio por rua
street_price_avg = df.groupby('STREET')['PRICE'].mean()

# Calcular a área média por rua
street_area_avg = df.groupby('STREET')['USABLEAREAS'].mean()

# Normalizar os preços e áreas para que fiquem entre 0 e 1
price_min, price_max = street_price_avg.min(), street_price_avg.max()
area_min, area_max = street_area_avg.min(), street_area_avg.max()

# Função de normalização
def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)

# Normalizar preço médio e área média por rua
normalized_price = street_price_avg.apply(lambda x: normalize(x, price_min, price_max))
normalized_area = street_area_avg.apply(lambda x: normalize(x, area_min, area_max))

# Calcular a relevância combinando preço e área (com uma média ponderada, por exemplo)
street_relevance = (normalized_price * 0.75) + (normalized_area * 0.25)

# Adicionar a coluna STREET_RELEVANCE ao DataFrame original
df['STREET_RELEVANCE'] = df['STREET'].map(street_relevance)

# Salvar o DataFrame atualizado no mesmo arquivo
df.to_csv(file_path, index=False)