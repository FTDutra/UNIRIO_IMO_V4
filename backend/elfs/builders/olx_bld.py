import os
import csv
import json
import logging
import pandas as pd

class OlxBuilder:
    def __init__(self, action=1, delete_after=True):
        """
        :param action: Define a ação que será realizada. [1] Gera o arquivo CSV temporário. [2] Gera o aquivo CSV composto. [3] Realiza as ações 1 e 2. [4] Não executa código automaticamente, permite edição manual.
        :param delete_after: Indica se o diretório temporário será apagado após as ações 2 ou 3. True por padrão
        """
        self._configure_logger()
        self.delete_after = delete_after

        # Configuração dos caminhos
        self.search_path = os.path.join("datacollection", "data")
        self.temp_folder = os.path.join("datacollection", "csv_temp", "olx")
        self.output_folder = os.path.join("datacollection", "csv")

        # Chama função para armazenar os arquivos
        self.files = self._read_files_memory()

        # Cria a pasta de saída final do arquivo
        os.makedirs(self.output_folder, exist_ok=True)

        if action == 1:
            self._run_step_one()

        elif action == 2:
            self._run_step_two()

        elif action == 3:
            self._run_step_one()
            self._run_step_two()


    def _run_step_one(self):
        # Cria a pasta temporária
        os.makedirs(self.temp_folder, exist_ok=True)
        self.process_files()

    def _run_step_two(self):
        # Cria a pasta de saída final do arquivo
        os.makedirs(self.output_folder, exist_ok=True)
        self.merge_csvs()
        if self.delete_after:
            self._cleanup_temp_folder()

    def _configure_logger(self):
        """Configura o logger para registro das operações executadas."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _cleanup_temp_folder(self):
        """Remove a pasta temporária e todo o seu conteúdo."""
        try:
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                os.remove(file_path)
            os.rmdir(self.temp_folder)
            self.logger.info(f"Pasta temporária {self.temp_folder} removida com sucesso.")
        except OSError as e:
            self.logger.error(f"Erro ao remover a pasta temporária {self.temp_folder}: {e}")

    def _read_files_memory(self):
        """
        Carrega os arquivos JSON disponíveis no diretório especificado para memória temporária.
        :return: Lista de nomes de arquivos JSON.
        """
        try:
            json_files = [f for f in os.listdir(self.search_path) if f.startswith("OLX_") and f.endswith(".json")]
            self.logger.info(f"{len(json_files)} arquivos encontrados no diretório.")
            return json_files
        except FileNotFoundError as ferror:
            self.logger.error(f"Falha ao carregar arquivos. Verifique o diretório: {ferror}")
            return []

    def return_file(self, file_name=None):
        """
        Lê o conteúdo de um arquivo JSON específico.
        :param file_name: Nome do arquivo. Se não fornecido, será usado um arquivo de exemplo.
        :return: Dados JSON do arquivo ou None em caso de erro.
        """
        file_path = os.path.join(self.search_path, file_name or "OLX_1_1.json")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.logger.info(f"Arquivo {file_name or 'padrão'} carregado com sucesso.")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Erro ao carregar o arquivo {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar o arquivo {file_path}: {e}")
        return None

    def save_to_csv(self, data, file_name):
        """
        Salva os dados em arquivo CSV. O nome do arquivo é passado sem a extensão.
        :param data: Dicionário contendo os dados a serem salvos.
        :param file_name: Nome do arquivo a ser tratado e salvo.
        """
        file_name = f"{file_name}.csv"
        file_path = os.path.join(self.temp_folder, file_name)

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
            self.logger.info(f"Arquivo CSV '{file_name}' salvo com sucesso!")
        except IOError as e:
            self.logger.error(f"Erro ao salvar o arquivo CSV: {e}")

    def build_content(self, data):
        """
        Monta um dicionário com os dados relevantes do JSON fornecido.
        :param data: Dados JSON extraídos da função return_file.
        :return: Dicionário com variáveis formatadas para o dataset.
        """
        if not data:
            self.logger.warning("Dados inválidos ou nulos fornecidos para build_content.")
            return {}

        # Detalhes gerais do imóvel
        general_details = {
            "type": data["category"],
            "neighborhood": data.get("locationDetails", {}).get("neighbourhood", "")
        }

        # Informações sobre preços
        price_builder = {
            "price": data["price"],
            "iptu": next((prop['value'] for prop in data["properties"] if prop['name'] == 'iptu'), None),
            "monthlyCondoFee": next((prop['value'] for prop in data["properties"] if prop['name'] == 'condominio'), None),
        }

        # Função para limpar e normalizar os valores de preço
        def clean_price(value):
            if isinstance(value, str):
                return value.replace("R$", "").replace(".", "").strip()
            return value

        # Normalizando todos os valores de 'general_details' e 'price_builder'
        general_details_cleaned = {key: clean_price(value) for key, value in general_details.items()}
        price_builder_cleaned = {key: clean_price(value) for key, value in price_builder.items()}

        # Detalhes do imóvel
        imo_details = {
            "usableAreas": next((prop['value'] for prop in data["properties"] if prop['name'] == 'size'), None),
            "totalAreas": next((prop['value'] for prop in data["properties"] if prop['name'] == 'size'), None),
            "parkingSpaces": next((prop['value'] for prop in data["properties"] if prop['name'] == 'garage_spaces'), None),
            "bathrooms": next((prop['value'] for prop in data["properties"] if prop['name'] == 'bathrooms'), None),
            "bedrooms": next((prop['value'] for prop in data["properties"] if prop['name'] == 'rooms'), None)
        }

        # Função para limpar e normalizar os valores de m2
        def clean_m2(value):
            if isinstance(value, str):
                return value.replace("m²", "").replace(".", "").strip()
            return value

        imo_details_cleaned = {key: clean_m2(value) for key, value in imo_details.items()}

        # Catura as características
        re_features = next((item['value'] for item in data.get("properties", []) if item['name'] == "re_features"), "")
        re_complex_features = next(
            (item['value'] for item in data.get("properties", []) if item['name'] == "re_complex_features"), "")

        # Transformando as características em listas
        re_features_list = re_features.split(",") if re_features else []
        re_complex_features_list = re_complex_features.split(",") if re_complex_features else []

        # Contagem total de características
        total_features = len(re_features_list) + len(re_complex_features_list)

        # Dados finais com amenidades incluídas
        imo_result_json = {
            **general_details_cleaned,
            **price_builder_cleaned,
            **imo_details_cleaned,
            "TOTAL_AMENITIES": total_features,
            **{feature.strip(): True for feature in re_features_list},
            **{feature.strip(): True for feature in re_complex_features_list}
        }

        self.logger.info("Dados formatados com sucesso.")
        return imo_result_json

    def process_files(self):
        """
        Itera sobre os arquivos JSON disponíveis, chama a função build_content para cada um
        e salva os resultados no CSV.
        """
        for file_name in self.files:
            try:
                file_path = os.path.join(self.search_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    imo = data
                    content = self.build_content(imo)
                    self.save_to_csv(data=content, file_name=file_name)
            except Exception as e:
                self.logger.error(f"Erro ao processar o arquivo {file_name}: {e}")

    def merge_csvs(self):
        """
        Mescla todos os CSVs temporários em único arquivo final.
        """
        try:
            df_list = []
            for arquivo in os.listdir(self.temp_folder):
                if arquivo.endswith(".csv"):
                    caminho_arquivo = os.path.join(self.temp_folder, arquivo)
                    df_temp = pd.read_csv(caminho_arquivo)
                    df_list.append(df_temp)

            # Concatena todos os DataFrames, alinhando pelas colunas
            df_final = pd.concat(df_list, axis=0, ignore_index=True, sort=False)
            filename = os.path.join(self.output_folder, "olx_col.csv")
            df_final.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Arquivo CSV final 'olx_col.csv' salvo com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao mesclar os arquivos CSV: {e}")