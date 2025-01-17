import io
import csv
import json
import torch
import numpy as np
import pandas as pd
from templates.controller import createJsonPrep as cjp

class HousePredict:
    def __init__(self):
        self.checkpoint_path = "static/model/house_price_model_updated.pth"
        self.json_file_path = "test/houses/house1.json"
        # self.cjp = cjp.CreateJsonPreparation()

    def _load_model(self):
        checkpoint = torch.load(self.checkpoint_path)
        input_size = checkpoint['scaler'].mean_.shape[0]
        hidden_units, num_layers, dropout_rate = 480, 2, 0.25

        layers = [
            torch.nn.Linear(input_size, hidden_units),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout_rate),
        ]
        for _ in range(num_layers - 1):
            layers.extend([
                torch.nn.Linear(hidden_units, hidden_units),
                torch.nn.ReLU(),
                torch.nn.Dropout(dropout_rate),
            ])
        layers.append(torch.nn.Linear(hidden_units, 1))
        model = torch.nn.Sequential(*layers)

        # Ajusta os nomes das chaves no estado do modelo
        state_dict = {k.replace("model.", ""): v for k, v in checkpoint["model_state_dict"].items()}
        model.load_state_dict(state_dict)
        model.eval()
        scaler = checkpoint["scaler"]
        return model, scaler

    def _json_to_csv_in_memory(self, json_content):
        if isinstance(json_content, str):
            data = json.loads(json_content)
        else:
            data = json_content

        data_values = data.get("DATA", {})
        if not data_values:
            raise ValueError("O JSON fornecido não contém a chave 'DATA' ou está vazio.")

        # Cria o buffer em memória para armazenar o CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(data_values.keys())  # Escreve os cabeçalhos
        writer.writerow(data_values.values())  # Escreve os valores
        output.seek(0)  # Retorna ao início do buffer para leitura posterior
        return output

    def _preprocess_data(self, csv_buffer, target_col="PRICE"):
        data = pd.read_csv(csv_buffer)
        numerical_features = data.select_dtypes(include=[float, int]).columns.tolist()
        data[numerical_features] = data[numerical_features].fillna(data[numerical_features].median())
        X = data.drop(target_col, axis=1, errors="ignore").select_dtypes(exclude=["object", "category"]).values
        return data, X

    def _predict(self, model, scaler, X):
        X_normalized = scaler.transform(X)
        X_tensor = torch.tensor(X_normalized, dtype=torch.float32)
        with torch.no_grad():
            return model(X_tensor).numpy()

    def predict(self, json_content=None):

        if json_content is not None:
            json_content = json_content
        else:
            with open(self.json_file_path, "r") as f:
                json_content = f.read()

        csv_buffer = self._json_to_csv_in_memory(json_content)

        model, scaler = self._load_model()
        _, X_new = self._preprocess_data(csv_buffer)

        price = self._predict(model, scaler, X_new)
        max_price = price * 1.2
        min_price = price * 0.8
        return price, max_price, min_price