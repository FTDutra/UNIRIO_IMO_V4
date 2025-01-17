#   ---------------------------------------------------------------------------------------------------------
# from scraper import olx_c
# OLX = olx_c.OlxDataCollector()
# OLX.collect_data()
#   ---------------------------------------------------------------------------------------------------------

import os
import json
import cloudscraper
from parsel import Selector

class OlxDataCollector:
    def __init__(self, output_dir=os.path.join("datacollection", "raw", "olximoveis")):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_results_to_file(self, results, page):
        """
        :param results: Resultado json da API
        :param page: Número da página. Necessário para montar o nome do arquivo
        """
        file_name = os.path.join(self.output_dir, f"{page}.json")
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        print(f"Página {page} salva em: {file_name}")

    def fetch_data_for_page(self, page):
        scraper = cloudscraper.create_scraper()
        r = scraper.get(
            f"https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro-e-regiao?f=c&rts=306&rts=302&rts=305&o={page}")
        response = Selector(text=r.text)

        results = json.loads(
            response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        )

        return results

    def collect_data(self, start_page=1, end_page=100):
        """
        :param start_page: Página inicial. Padrão 1
        :param end_page: Página final: 101 (100 + 1)
        """
        for page in range(start_page, end_page + 1):
            try:
                results = self.fetch_data_for_page(page)
                self.save_results_to_file(results, page)
            except Exception as e:
                print(f"Erro ao processar a página {page}: {e}")