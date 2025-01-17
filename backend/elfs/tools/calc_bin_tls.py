# Não sei se vou incorporar como método do projeto
# Fiz para testar a disposição dos preços dos imóveis

import pandas as pd
import os
import numpy as np  # Importando o numpy para usar linspace

# Carregar o arquivo CSV
file_path = 'datacollection/csv/collection_wt_multicol.csv'
data = pd.read_csv(file_path)

# Definir o número de bins desejados
num_bins = 40

# Calcular o range do preço (mínimo e máximo)
price_min = data['PRICE'].min()
price_max = data['PRICE'].max()

# Criar os intervalos (bins) com base no range do preço
bin_edges = np.linspace(price_min, price_max, num_bins + 1)

# Atribuir cada imóvel a um bin com base no preço
data['PRICE_BIN'] = pd.cut(data['PRICE'], bins=bin_edges, labels=[f'Bin_{i+1}' for i in range(num_bins)], include_lowest=True)

# Criar diretório base para salvar os arquivos
base_dir = './datacollection/csv/bins/'
os.makedirs(base_dir, exist_ok=True)

# Salvar os dados de cada bin em arquivos CSV
for bin_label in data['PRICE_BIN'].unique():
    bin_data = data[data['PRICE_BIN'] == bin_label]
    file_path = os.path.join(base_dir, f'{bin_label}.csv')
    bin_data.to_csv(file_path, index=False)
    print(f"Arquivo salvo: {file_path}")

# Mostrar os limites dos bins
print("Limites dos Bins (Preço):", bin_edges)