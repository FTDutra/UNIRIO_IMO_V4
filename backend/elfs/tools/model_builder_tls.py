"""
=====================================================================================================
Este trecho do código faz a atualização do modelo com base em novas épocas
=====================================================================================================
"""

# import numpy as np
# import torch
# import torch.nn as nn
# import torch.optim as optim
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import mean_squared_error, mean_absolute_error
#
# # Carregar os dados
# file_path = "datacollection/csv/bins/Bin_1.csv"  # Substitua pelo caminho do seu CSV
# data = pd.read_csv(file_path)
#
# # Identificar colunas numéricas
# numerical_features = data.select_dtypes(include=[np.number]).columns.tolist()
#
# # Tratar valores nulos APENAS em colunas numéricas
# data.loc[:, numerical_features] = data.loc[:, numerical_features].fillna(data.loc[:, numerical_features].median())
#
# # Remover colunas categóricas (do tipo object ou category)
# data = data.select_dtypes(exclude=['object', 'category'])
#
# # Assumindo que a última coluna seja o preço de imóvel (alvo)
# X = data.drop('PRICE', axis=1).values  # Substitua 'preco' pelo nome da coluna de preço
# y = data['PRICE'].values  # Substitua 'preco' pelo nome da coluna de preço
#
# # Dividir em treino e teste
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # Normalizar os dados
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_test = scaler.transform(X_test)
#
# # Converter para tensores do PyTorch
# X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
# X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
# y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
# y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)
#
# # Definir o modelo
# class HousePriceModel(nn.Module):
#     def __init__(self, input_size, hidden_units, num_layers, dropout_rate):
#         super(HousePriceModel, self).__init__()
#         self.hidden_units = hidden_units
#         self.num_layers = num_layers
#         self.dropout_rate = dropout_rate
#
#         # Camadas da rede
#         layers = []
#         layers.append(nn.Linear(input_size, self.hidden_units))
#         layers.append(nn.ReLU())
#         layers.append(nn.Dropout(self.dropout_rate))
#
#         # Adicionar camadas ocultas
#         for _ in range(self.num_layers - 1):
#             layers.append(nn.Linear(self.hidden_units, self.hidden_units))
#             layers.append(nn.ReLU())
#             layers.append(nn.Dropout(self.dropout_rate))
#
#         # Camada de saída
#         layers.append(nn.Linear(self.hidden_units, 1))
#
#         self.model = nn.Sequential(*layers)
#
#     def forward(self, x):
#         return self.model(x)
#
# # Inicializar o modelo
# input_size = X_train.shape[1]  # Número de características de entrada
# hidden_units = 480
# num_layers = 2
# dropout_rate = 0.25193649347473823
# model = HousePriceModel(input_size, hidden_units, num_layers, dropout_rate)
#
# # Definir a função de perda e o otimizador
# learning_rate = 0.002918542020635498
# criterion = nn.MSELoss()  # Mean Squared Error para regressão
# optimizer = optim.Adam(model.parameters(), lr=learning_rate)
#
# # Treinamento
# num_epochs = 1000  # Defina o número de épocas conforme necessário
# for epoch in range(num_epochs):
#     # Passo para frente (forward pass)
#     y_pred = model(X_train_tensor)
#
#     # Calcular a perda
#     loss = criterion(y_pred, y_train_tensor)
#
#     # Passo para trás (backward pass)
#     optimizer.zero_grad()  # Limpar os gradientes anteriores
#     loss.backward()  # Calcular os gradientes
#     optimizer.step()  # Atualizar os pesos
#
#     # Exibir a perda a cada 100 épocas
#     if (epoch + 1) % 100 == 0:
#         # Calcular o MAE para o conjunto de treinamento
#         mae_train = mean_absolute_error(y_train_tensor.detach().numpy(), y_pred.detach().numpy())
#         print(f'Epoch [{epoch + 1}/{num_epochs}], Loss (MSE): {loss.item():.4f}, MAE: {mae_train:.4f}')
#
# # Avaliação do modelo no conjunto de teste (Val Loss)
# model.eval()  # Colocar o modelo em modo de avaliação
# with torch.no_grad():  # Desligar o cálculo de gradientes para eficiência
#     y_test_pred = model(X_test_tensor)
#     test_loss = mean_squared_error(y_test_tensor, y_test_pred)
#     mae_test = mean_absolute_error(y_test_tensor.numpy(), y_test_pred.numpy())
#     print(f'Test MSE: {test_loss:.4f}')
#     print(f'Test MAE: {mae_test:.4f}')
#
# # Salvar o modelo completo
# torch.save({
#     'model_state_dict': model.state_dict(),
#     'optimizer_state_dict': optimizer.state_dict(),
#     'scaler': scaler,  # Salvar o scaler para normalizar os novos dados
# }, 'house_price_model.pth')
# print("Modelo salvo com sucesso!")

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Classe do modelo
class HousePriceModel(nn.Module):
    def __init__(self, input_size, hidden_units, num_layers, dropout_rate):
        super(HousePriceModel, self).__init__()
        self.hidden_units = hidden_units
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate

        # Camadas da rede
        layers = []
        layers.append(nn.Linear(input_size, self.hidden_units))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(self.dropout_rate))

        # Adicionar camadas ocultas
        for _ in range(self.num_layers - 1):
            layers.append(nn.Linear(self.hidden_units, self.hidden_units))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(self.dropout_rate))

        # Camada de saída
        layers.append(nn.Linear(self.hidden_units, 1))

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)


# Carregar os dados
file_path = "datacollection/csv/bins/Bin_1.csv"  # Substitua pelo caminho do seu CSV
data = pd.read_csv(file_path)

# Identificar colunas numéricas
numerical_features = data.select_dtypes(include=[np.number]).columns.tolist()

# Tratar valores nulos APENAS em colunas numéricas
data.loc[:, numerical_features] = data.loc[:, numerical_features].fillna(data.loc[:, numerical_features].median())

# Remover colunas categóricas (do tipo object ou category)
data = data.select_dtypes(exclude=['object', 'category'])

# Assumindo que a última coluna seja o preço de imóvel (alvo)
X = data.drop('PRICE', axis=1).values  # Substitua 'PRICE' pelo nome da coluna de preço
y = data['PRICE'].values  # Substitua 'PRICE' pelo nome da coluna de preço

# Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preparar o scaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Converter para tensores do PyTorch
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

# Configurações do modelo
input_size = X_train.shape[1]  # Número de características de entrada
hidden_units = 480
num_layers = 2
dropout_rate = 0.25193649347473823
learning_rate = 0.002918542020635498

# Carregar o modelo salvo
checkpoint_path = 'house_price_model_updated.pth'  # Caminho para o modelo salvo
checkpoint = torch.load(checkpoint_path)

# Inicializar o modelo
model = HousePriceModel(input_size, hidden_units, num_layers, dropout_rate)
model.load_state_dict(checkpoint['model_state_dict'])

# Restaurar o otimizador
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

# Restaurar o scaler salvo
scaler = checkpoint['scaler']

# Função de perda
criterion = nn.MSELoss()  # Mean Squared Error para regressão

# Continuar o treinamento
num_epochs_continue = 50000  # Número de épocas adicionais
for epoch in range(num_epochs_continue):
    model.train()  # Garantir que o modelo esteja em modo de treinamento
    y_pred = model(X_train_tensor)  # Previsões do modelo
    loss = criterion(y_pred, y_train_tensor)  # Calcular a perda

    optimizer.zero_grad()  # Limpar gradientes
    loss.backward()  # Backpropagation
    optimizer.step()  # Atualizar os pesos

    # Exibir métricas a cada 100 épocas
    if (epoch + 1) % 100 == 0:
        with torch.no_grad():
            mae_train = mean_absolute_error(y_train_tensor.numpy(), y_pred.numpy())
        print(f'Epoch [{epoch + 1}/{num_epochs_continue}], Loss (MSE): {loss.item():.4f}, MAE: {mae_train:.4f}')

# Avaliação no conjunto de teste
model.eval()  # Colocar o modelo em modo de avaliação
with torch.no_grad():
    y_test_pred = model(X_test_tensor)
    test_loss = mean_squared_error(y_test_tensor.numpy(), y_test_pred.numpy())
    mae_test = mean_absolute_error(y_test_tensor.numpy(), y_test_pred.numpy())
    print(f'Test MSE: {test_loss:.4f}')
    print(f'Test MAE: {mae_test:.4f}')

# Salvar o modelo atualizado
updated_checkpoint_path = 'house_price_model_updated_2.pth'
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'scaler': scaler,
}, updated_checkpoint_path)
print("Modelo atualizado salvo com sucesso!")



"""
=====================================================================================================
Este trecho do código faz a efetiva predição do preço do imóvel a partir do modelo criado
=====================================================================================================
"""

# import torch
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import r2_score, mean_absolute_error
#
#
# # Definir o modelo (mesmo do treinamento)
# class HousePriceModel(torch.nn.Module):
#     def __init__(self, input_size, hidden_units, num_layers, dropout_rate):
#         super(HousePriceModel, self).__init__()
#         layers = [torch.nn.Linear(input_size, hidden_units), torch.nn.ReLU(), torch.nn.Dropout(dropout_rate)]
#         for _ in range(num_layers - 1):
#             layers.extend(
#                 [torch.nn.Linear(hidden_units, hidden_units), torch.nn.ReLU(), torch.nn.Dropout(dropout_rate)])
#         layers.append(torch.nn.Linear(hidden_units, 1))
#         self.model = torch.nn.Sequential(*layers)
#
#     def forward(self, x):
#         return self.model(x)
#
#
# # Função para carregar o modelo salvo
# def load_model(checkpoint_path):
#     checkpoint = torch.load(checkpoint_path)
#     input_size = checkpoint['scaler'].mean_.shape[0]  # Obtém o número de recursos do scaler
#     hidden_units = 480  # Mesmo valor usado no treinamento
#     num_layers = 2
#     dropout_rate = 0.25193649347473823
#     model = HousePriceModel(input_size, hidden_units, num_layers, dropout_rate)
#     model.load_state_dict(checkpoint['model_state_dict'])
#     model.eval()  # Modo de avaliação
#     scaler = checkpoint['scaler']  # Recupera o scaler para normalizar os dados
#     return model, scaler
#
#
# # Função para fazer predições e exibir resultados
# def predict_and_display(file_path, checkpoint_path, target_col='PRICE'):
#     # Configuração do pandas para exibir sem notação científica
#     pd.options.display.float_format = '{:.2f}'.format
#
#     # Carregar o modelo e o scaler
#     model, scaler = load_model(checkpoint_path)
#
#     # Carregar os novos dados
#     new_data = pd.read_csv(file_path)
#
#     # Pré-processar os dados
#     numerical_features = new_data.select_dtypes(include=[float, int]).columns.tolist()
#     new_data.loc[:, numerical_features] = new_data.loc[:, numerical_features].fillna(
#         new_data.loc[:, numerical_features].median())
#     X_new = new_data.select_dtypes(exclude=['object', 'category']).drop(target_col, axis=1, errors='ignore').values
#
#     # Normalizar os dados
#     X_new_normalized = scaler.transform(X_new)
#
#     # Converter para tensor PyTorch
#     X_new_tensor = torch.tensor(X_new_normalized, dtype=torch.float32)
#
#     # Realizar predições
#     with torch.no_grad():
#         predictions = model(X_new_tensor).numpy()
#
#     # Criar DataFrame para exibir os resultados
#     if target_col in new_data.columns:
#         results = pd.DataFrame({
#             "PRICE": new_data[target_col],
#             "PREDICTED PRICE": predictions.flatten(),
#         })
#         # Adicionar coluna da diferença
#         results["DIFFERENCE"] = results["PREDICTED PRICE"] - results["PRICE"]
#
#         # Calcular o percentual de erro
#         results["PERCENT ERROR (%)"] = (results["DIFFERENCE"] / results["PRICE"].abs()) * 100
#
#         # Calcular intervalo com erro para menos e para mais
#         results["LOWER ERROR"] = results["PREDICTED PRICE"] * (1 - abs(results["PERCENT ERROR (%)"] / 100))
#         results["UPPER ERROR"] = results["PREDICTED PRICE"] * (1 + abs(results["PERCENT ERROR (%)"] / 100))
#
#         # Calcular métricas
#         r2 = r2_score(results["PRICE"], results["PREDICTED PRICE"])
#         mae = mean_absolute_error(results["PRICE"], results["PREDICTED PRICE"])
#         print(f"R²: {r2:.4f}")
#         print(f"Média de Erro Absoluto (MAE): {mae:.2f}")
#     else:
#         results = pd.DataFrame({
#             "PREDICTED PRICE": predictions.flatten()
#         })
#
#     # Selecionar apenas 20 primeiras linhas
#     results = results.head(20)
#
#     print(results.to_string(index=False))  # Exibir resultados sem o índice
#
#
# # Caminho para o CSV e o modelo salvo
# file_path = "datacollection/csv/bins/Bin_1.csv"  # Substitua pelo caminho do CSV com novos dados
# checkpoint_path = "house_price_model_updated.pth"  # Caminho para o modelo salvo
#
# # Fazer predições e exibir resultados
# predict_and_display(file_path, checkpoint_path)


"""
=====================================================================================================
Este trecho do código faz a verificação das features que foram obtidas pelo modelo
=====================================================================================================
"""

# import torch
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib
# import seaborn as sns
#
# matplotlib.use('tkagg')
#
# # Definir o modelo (mesmo do treinamento)
# class HousePriceModel(torch.nn.Module):
#     def __init__(self, input_size, hidden_units, num_layers, dropout_rate):
#         super(HousePriceModel, self).__init__()
#         layers = [torch.nn.Linear(input_size, hidden_units), torch.nn.ReLU(), torch.nn.Dropout(dropout_rate)]
#         for _ in range(num_layers - 1):
#             layers.extend([torch.nn.Linear(hidden_units, hidden_units), torch.nn.ReLU(), torch.nn.Dropout(dropout_rate)])
#         layers.append(torch.nn.Linear(hidden_units, 1))
#         self.model = torch.nn.Sequential(*layers)
#
#     def forward(self, x):
#         return self.model(x)
#
# # Função para carregar o modelo salvo
# def load_model(checkpoint_path):
#     checkpoint = torch.load(checkpoint_path)
#     input_size = checkpoint['scaler'].mean_.shape[0]  # Obtém o número de recursos do scaler
#     hidden_units = 480  # Mesmo valor usado no treinamento
#     num_layers = 2
#     dropout_rate = 0.25193649347473823
#     model = HousePriceModel(input_size, hidden_units, num_layers, dropout_rate)
#     model.load_state_dict(checkpoint['model_state_dict'])
#     model.eval()  # Modo de avaliação
#     scaler = checkpoint['scaler']  # Recupera o scaler para normalizar os dados
#     return model, scaler
#
# # Função para identificar e exibir as features mais relevantes
# def identify_relevant_features(file_path, checkpoint_path):
#     # Carregar o modelo e o scaler
#     model, scaler = load_model(checkpoint_path)
#
#     # Carregar os dados para obter os nomes das features
#     data = pd.read_csv(file_path)
#
#     # Identificar as colunas numéricas (features utilizadas)
#     numerical_features = data.select_dtypes(include=[float, int]).columns.tolist()
#     if 'PRICE' in numerical_features:
#         numerical_features.remove('PRICE')  # Remover a coluna alvo se presente
#
#     # Obter os pesos da primeira camada linear
#     first_layer_weights = model.model[0].weight.detach().numpy().flatten()
#
#     print(f"Number of numerical features: {len(numerical_features)}")
#     print(f"Number of weights: {len(first_layer_weights)}")
#
#     model_features = numerical_features[:len(first_layer_weights)]
#     first_layer_weights = first_layer_weights[:len(model_features)]  # Ajustar comprimento, se necessário
#
#     # Criar um DataFrame para exibir as features e seus pesos absolutos (importância)
#     feature_importance = pd.DataFrame({
#         "Feature": model_features,
#         "Weight": np.abs(first_layer_weights)
#     })
#
#     # Ordenar pelas features mais relevantes (maior peso absoluto)
#     feature_importance = feature_importance.sort_values(by="Weight", ascending=False)
#
#     print("Features mais relevantes:")
#     print(feature_importance.to_string(index=False))
#
#     # Plotando as features mais relevantes
#     plt.figure(figsize=(10, 6))
#     sns.barplot(x="Weight", y="Feature", data=feature_importance.head(20))  # Mostrando as 20 mais relevantes
#     plt.title("Features Mais Relevantes - Importância dos Pesos")
#     plt.xlabel("Peso Absoluto")
#     plt.ylabel("Feature")
#     plt.show()
#
# # Caminho para o CSV e o modelo salvo
# file_path = "datacollection/csv/bins/Bin_1.csv"  # Substitua pelo caminho do CSV com dados
# checkpoint_path = "house_price_model_updated.pth"  # Caminho para o modelo salvo
#
# # Identificar e exibir as features mais relevantes
# identify_relevant_features(file_path, checkpoint_path)