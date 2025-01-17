import os
import json
import logging

class OlxSplitter:
    def __init__(self,
                 input_folder="datacollection/raw/olximoveis",
                 output_folder="datacollection/data"):
        """
        Inicializa a classe com os caminhos para a pasta de entrada e saída.
        Caso a pasta de saída não exista, será criada.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder
        # Configuração do logger
        self._configure_logger()
        # ----------------------------------------------------------------------

        # Verificar se a pasta de saída existe, se não, cria
        os.makedirs(self.output_folder, exist_ok=True)

        # Processa os arquivos da pasta de entrada
        self._process_files_in_folder(self.input_folder)

    def _configure_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _is_advertisement_valid(self, ad):
        """
        Valida os anúncios, ignorando aqueles com dados indesejados.
        """
        return not (
                ad.get("advertisingId") == "advertising-msite-listing-native-direct" and
                ad.get("deviceType") == "msite"
        )

    def _save_ads_to_files(self, ads, base_filename):
        """
        Salva os anúncios válidos em arquivos JSON.
        """
        valid_ads_count = 0

        for idx, ad in enumerate(ads, 1):
            if self._is_advertisement_valid(ad):
                valid_ads_count += 1
                filename = os.path.join(self.output_folder, f"{base_filename}_{idx}.json")

                try:
                    with open(filename, "w", encoding="utf-8") as file:
                        json.dump(ad, file, ensure_ascii=False, indent=4)
                    self.logger.info(f"Arquivo {filename} salvo com sucesso!")
                except IOError as e:
                    self.logger.error(f"Erro ao salvar o arquivo {filename}: {e}")
                    return False
            else:
                self.logger.info(f"Anúncio ignorado devido ao conteúdo indesejado.")

        if valid_ads_count == 0:
            self.logger.warning(f"Nenhum anúncio válido encontrado para salvar no arquivo {base_filename}.")
            return False

        return True

    def _process_files_in_folder(self, folder_path):
        """
        Processa todos os arquivos JSON na pasta especificada.
        """
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                except (IOError, json.JSONDecodeError) as e:
                    self.logger.error(f"Erro ao ler o arquivo {file_path}: {e}")
                    continue

                ads = data.get("props", {}).get("pageProps", {}).get("ads", [])

                if ads:
                    base_filename = f"OLX_{filename[:-5]}"  # Remover a extensão ".json"
                    self._save_ads_to_files(ads, base_filename)
                else:
                    self.logger.info(f"Sem anúncios no arquivo {filename}.")