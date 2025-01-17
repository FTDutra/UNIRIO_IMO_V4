import os
import csv
import json
import logging
import pandas as pd

class ZapimoveisBuilder:
    def __init__(self, action=1, delete_after=True):
        """
        :param action: Define a ação que será realizada. [1] Gera o arquivo CSV temporário. [2] Gera o aquivo CSV composto. [3] Realiza as ações 1 e 2. [4] Não executa código automaticamente, permite edição manual.
        :param delete_after: Indica se o diretório temporário será apagado após as ações 2 ou 3. True por padrão
        """
        self._configure_logger()
        self.delete_after = delete_after

        # Configuração dos caminhos
        self.search_path = os.path.join("datacollection", "data")
        self.temp_folder = os.path.join("datacollection", "csv_temp", "zapimoveis")
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
            json_files = [f for f in os.listdir(self.search_path) if f.startswith("zapimoveis_") and f.endswith(".json")]
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
                return data.get("listing")
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
            "type": data.get("unitTypes", [None])[0],
            "zone": data.get("address", {}).get("zone", ""),
            "neighborhood": data.get("address", {}).get("neighborhood", ""),
            "street": data.get("address", {}).get("street", ""),
        }

        # Informações sobre preços
        pricing_info = data.get("pricingInfos", [{}])[0]
        price_builder = {
            "price": pricing_info.get("price", 0),
            "iptu": pricing_info.get("yearlyIptu", 0),
            "monthlyCondoFee": pricing_info.get("monthlyCondoFee", 0),
        }

        # Detalhes do imóvel
        imo_details = {
            "usableAreas": data.get("usableAreas", [0])[0] if data.get("usableAreas") else 0,
            # "usableAreas": data.get("usableAreas", [0])[0],
            "totalAreas": data.get("totalAreas", [0])[0] if data.get("totalAreas") else 0,
            # "totalAreas": data.get("totalAreas", [0])[0],
            "parkingSpaces": data.get("parkingSpaces", [0])[0] if data.get("parkingSpaces") else 0,
            "suites": data.get("suites", [0])[0] if data.get("suites") else 0,
            # "suites": data.get("suites", [0])[0],
            "bathrooms": data.get("bathrooms", [0])[0] if data.get("bathrooms") else 0,
            # "bathrooms": data.get("bathrooms", [0])[0],
            "bedrooms": data.get("bedrooms", [0])[0] if data.get("bedrooms") else 0,
            # "bedrooms": data.get("bedrooms", [0])[0],
        }

        amenities = data.get("amenities")
        if not isinstance(amenities, list):
            amenities = []
        # Contagem do número total de amenidades
        total_amenities = len(amenities)

        # Dados finais com amenidades incluídas
        imo_result_json = {
            **general_details,
            **price_builder,
            **imo_details,
            "TOTAL_AMENITIES": total_amenities,
            **{amenity: True for amenity in amenities}
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
                    imo = data.get("listing", {})
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
            filename = os.path.join(self.output_folder, "zapimoveis_col.csv")
            df_final.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Arquivo CSV final 'zapimoveis_col.csv' salvo com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao mesclar os arquivos CSV: {e}")