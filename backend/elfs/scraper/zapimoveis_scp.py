#   ---------------------------------------------------------------------------------------------------------
#   Exemplo de chamada
#   collector = ZapImoveisDataCollector()
#   collector.collect_data()
#   ---------------------------------------------------------------------------------------------------------

import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient

class ZapImoveisDataCollector:
    def __init__(self,
                 api_key_env_var="ZAPIMOVEIS_APIFY_API_KEY",
                 output_dir=os.path.join("datacollection", "raw", "zapimoveis")):
        """
        :param api_key_env_var: Instancia a chave API ZapImóveis disponível no .env
        :param output_dir: Caminho de saída dos arquivos já em json
        """
        load_dotenv()
        self.api_key = os.getenv(api_key_env_var)
        if not self.api_key:
            raise ValueError(f"A chave da API não foi definida. Configure a variável de ambiente '{api_key_env_var}'.")

        self.client = ApifyClient(self.api_key)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_data_for_page(self, page, actor_id="1WyG7WWJM9Qjhmh1y", run_input_params=None):
        if run_input_params is None:
            run_input_params = {
                "type": "SALE",
                "city": "Rio de Janeiro",
                "state": "Rio de Janeiro",
                "unitType": "APARTMENT",
                "unitUsage": "RESIDENTIAL",
            }

        run_input = {**run_input_params, "page": page}
        run = self.client.actor(actor_id).call(run_input=run_input)
        results = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
        return results

    def save_results_to_file(self, results, page):
        """
        :param results: Resultado json da API
        :param page: Número da página. Necessário para montar o nome do arquivo
        """
        file_name = os.path.join(self.output_dir, f"{page}.json")
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        print(f"Página {page} salva em: {file_name}")

    def collect_data(self, start_page=1, end_page=100):
        """
        :param start_page: Página inicial. Padrão 1
        :param end_page: Página final: 100
        """
        for page in range(start_page, end_page + 1):
            try:
                results = self.fetch_data_for_page(page)
                self.save_results_to_file(results, page)
            except Exception as e:
                print(f"Erro ao processar a página {page}: {e}")