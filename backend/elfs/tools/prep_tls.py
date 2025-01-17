import os
import csv
import random
import logging

class DataPreparation:
    def __init__(self,
                 directory_path = None,
                 file_name = None,
                 validate_p = None):
        self._configure_logger()

        self.path = directory_path or os.path.join("datacollection", "csv")
        file_name = file_name or "collection_adj_aggr.csv"
        self.data = os.path.join(self.path, file_name)
        self.validate = (validate_p / 100) if validate_p is not None else 0.1

    def _configure_logger(self):
        """
        Configura o logger para registro das operações executadas.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def data_prep(self):
        """
        Método para processar e preparar os dados do arquivo CSV.
        Este método divide 10% dos dados e salva em um novo arquivo CSV.
        Remove as linhas de validação do arquivo original.
        """
        if not os.path.exists(self.data):
            self.logger.error(f"Arquivo {self.data} não encontrado.")
            return None

        try:
            # Lendo o arquivo CSV
            with open(self.data, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
                total_data = len(data)
                sample_size = int(total_data * self.validate)

                # Selecionando uma amostra aleatória de 10% dos dados
                sampled_data = random.sample(data, sample_size)

                # Removendo os dados amostrados do conjunto original
                remaining_data = [row for row in data if row not in sampled_data]

                # Salvando os dados de validação em um novo arquivo
                validation_file = os.path.join(self.path, "data_validation.csv")
                with open(validation_file, mode='w', newline='', encoding='utf-8') as validation_csv:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(validation_csv, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(sampled_data)

                # Salvando os dados restantes de volta no arquivo original
                with open(self.data, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(remaining_data)

                self.logger.info(f"{self.validate * 100}% dos dados foram extraídos e salvos em {validation_file}.")
                return sampled_data

        except Exception as e:
            self.logger.error(f"Erro ao processar o arquivo {self.data}: {e}")
            return None
