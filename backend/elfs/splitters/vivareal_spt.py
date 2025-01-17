import os
import json
import random
import string
import logging

class VivarealSplitter:
    def __init__(self, input_folder="datacollection/raw/vivareal",
                 temp_folder="datacollection/temp_har",
                 output_folder="datacollection/data",
                 action=1,
                 delete_after=True):
        """
        Inicializa a classe VivarealSplitter com os diretórios de entrada, temporário e saída.
        Caso necessário, cria as pastas especificadas.

        :param input_folder: Caminho da pasta de entrada.
        :param temp_folder: Caminho da pasta temporária.
        :param output_folder: Caminho da pasta de saída.
        :param action: Define qual ação será executada. [1] Cria estrutura json temporária a partir do arquivo .har. [2] Cria json dos anúncios individuais a partir do json temporário. [3] Realiza toda a operação.
        :param delete_after: Define se, nas opções 2 e 3 haverá a exclusão da pasta temporária.
        """
        self.input_folder = input_folder
        self.temp_folder = temp_folder
        self.output_folder = output_folder
        self.delete_after = delete_after
        self._configure_logger()

        if action == 1:
            self.TARGET_AUTHORITY = 'glue-api.vivareal.com'
            self._run_structure_constructor()

        elif action == 2:
            self.START_PATTERN = '{"search":{"result":{"listings":'
            self._run_ads_capture_splitter()

        elif action == 3:
            self._run_structure_constructor()
            self._run_ads_capture_splitter()

    def _run_structure_constructor(self):
        os.makedirs(self.temp_folder, exist_ok=True)
        self._process_pages_in_har()


    def _run_ads_capture_splitter(self):
        os.makedirs(self.output_folder, exist_ok=True)
        self._process_listings()
        if self.delete_after:
            self._cleanup_temp_folder()

    def _configure_logger(self):
        """
        Configura o logger para registro das operações executadas.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _cleanup_temp_folder(self):
        """
        Remove a pasta temporária e todo o seu conteúdo.
        """
        try:
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                os.remove(file_path)
            os.rmdir(self.temp_folder)
            self.logger.info(f"Pasta temporária {self.temp_folder} removida com sucesso.")
        except OSError as e:
            self.logger.error(f"Erro ao remover a pasta temporária {self.temp_folder}: {e}")

    def _load_json_file(self, file_path):
        """
        Carrega o conteúdo de um arquivo JSON, tratando possíveis erros.

        :param file_path: Caminho do arquivo JSON.
        :return: Dados carregados ou None em caso de erro.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {file_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON no arquivo {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Erro desconhecido ao carregar o arquivo {file_path}: {e}")
        return None

    def _save_json_file(self, data, file_path):
        """
        Salva dados em um arquivo JSON.

        :param data: Dados a serem salvos.
        :param file_path: Caminho do arquivo JSON.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            self.logger.info(f"Arquivo salvo: {file_path}")
        except IOError as e:
            self.logger.error(f"Erro ao salvar o arquivo {file_path}: {e}")

    def _filter_har_entries(self, har_data):
        """
        Filtra as entradas de um arquivo HAR pelo cabeçalho ":authority".

        :param har_data: Dados carregados do arquivo HAR.
        :return: Lista de entradas filtradas.
        """
        try:
            entries = har_data.get('log', {}).get('entries', [])
            if not entries:
                self.logger.warning("Nenhuma entrada encontrada no arquivo HAR.")
            return [
                entry for entry in entries
                if any(
                    header.get('name', '').lower() == ':authority' and header.get('value') == self.TARGET_AUTHORITY
                    for header in entry.get('request', {}).get('headers', [])
                )
            ]
        except AttributeError as e:
            self.logger.error(f"Estrutura inesperada no HAR: {e}")
            return []

    def _process_pages_in_har(self):
        """
        Processa arquivos HAR na pasta de entrada, filtrando e salvando páginas relevantes.
        """
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".har"):
                file_path = os.path.join(self.input_folder, filename)
                har_data = self._load_json_file(file_path)
                if har_data is None:
                    continue

                filtered_entries = self._filter_har_entries(har_data)
                base_filename = os.path.splitext(filename)[0]

                for idx, entry in enumerate(filtered_entries, start=1):
                    page_file = os.path.join(self.temp_folder, f"{base_filename}_{idx}.json")
                    text = entry.get('response', {}).get('content', {}).get('text', '')
                    if text:
                        try:
                            json_data = json.loads(text)
                            self._save_json_file(json_data, page_file)
                        except json.JSONDecodeError:
                            self.logger.error(f"Erro ao decodificar JSON em uma entrada filtrada do HAR: {page_file}")

    def _generate_random_hash(self, length=10):
        """
        Gera um hash aleatório com letras minúsculas e números.
        """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _process_listings(self):
        """
        Processa arquivos JSON na pasta temporária, extraindo e salvando anúncios.
        """
        for filename in os.listdir(self.temp_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(self.temp_folder, filename)
                data = self._load_json_file(file_path)
                if data is None:
                    continue

                listings = data.get("search", {}).get("result", {}).get("listings", [])
                if listings:
                    for idx, listing in enumerate(listings, start=1):
                        hash = self._generate_random_hash(length=8)
                        listing_file = os.path.join(self.output_folder, f"vivareal_{hash}.json")
                        self._save_json_file(listing, listing_file)