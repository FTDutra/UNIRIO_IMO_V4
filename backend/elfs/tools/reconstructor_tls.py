# Exemplo de chamada e uso
# from elfs.tools import reconstructor_tls
#
# rectls = reconstructor_tls.ReconstructorTool()
# rectls.reconstruir_pasta_csv()

import os
import shutil
import logging
from elfs.builders import builders


class ReconstructorTool:
    def __init__(self):
        """
        Inicializa a classe com o diretório principal e configura o logger.
        :param directory_domain: Caminho para o diretório que será gerenciado.
        """
        self.directory_domain = os.path.join("datacollection", "csv")
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _verificar_arquivos_obrigatorios(self, temp_folder):
        """
        Verifica se os arquivos obrigatórios estão presentes na pasta temporária.
        Se algum arquivo estiver ausente, chama o builder para gerar o arquivo.
        :param temp_folder: Caminho da pasta temporária.
        """
        obrigatorios = ["olx", "vivareal", "zapimoveis"]

        for arquivo in obrigatorios:
            arquivo_path = os.path.join(temp_folder, arquivo)
            if not os.path.exists(arquivo_path):
                self.logger.warning(f"Arquivo obrigatório {arquivo} não encontrado na pasta temporária.")
                self.logger.info("Iniciando o builder para gerar o arquivo faltante.")
                builder = builders.Builders()
                builder.executar_builder(builder=arquivo, action=2, delete_after=False)
                self.logger.info(f"Arquivo {arquivo} gerado com sucesso.")

    def _limpar_pasta_csv(self):
        """
        Limpa todos os arquivos da pasta CSV antes de gerar os arquivos obrigatórios,
        caso a pasta temporária não exista.
        :return: None
        """
        if os.path.exists(self.directory_domain):
            for file_name in os.listdir(self.directory_domain):
                file_path = os.path.join(self.directory_domain, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            self.logger.info("Todos os arquivos da pasta CSV foram removidos.")

    def reconstruir_pasta_csv(self):
        """
        Reconstrói a pasta principal movendo os arquivos da pasta temporária de volta
        e removendo o arquivo collection.csv, se existir.
        Verifica se os arquivos obrigatórios estão presentes e chama o builder se necessário.
        :return: True se o processo for bem-sucedido, False em caso de erro.
        """
        temp_folder = os.path.join(self.directory_domain, "ignore")

        try:
            if not os.path.exists(temp_folder):
                self.logger.info(
                    "A pasta temporária 'ignore' não existe. Limpando a pasta CSV e gerando arquivos obrigatórios.")

                # Se a pasta não existir, limpar a pasta CSV e gerar os arquivos obrigatórios
                self._limpar_pasta_csv()
                self.logger.info("Pasta CSV limpa com sucesso.")

                # Gerar arquivos obrigatórios
                self._verificar_arquivos_obrigatorios(self.directory_domain)

            else:
                self._verificar_arquivos_obrigatorios(temp_folder)

                # Mover os arquivos da pasta temporária para a pasta original
                for file_name in os.listdir(temp_folder):
                    file_path = os.path.join(temp_folder, file_name)
                    shutil.move(file_path, os.path.join(self.directory_domain, file_name))

                # Remover a pasta temporária se estiver vazia
                os.rmdir(temp_folder)
                self.logger.info("Arquivos foram movidos da pasta temporária para a pasta original.")

            # Remover o arquivo collection.csv, se existir
            collection_file = os.path.join(self.directory_domain, "collection.csv")
            if os.path.exists(collection_file):
                os.remove(collection_file)
                self.logger.info("Arquivo collection.csv foi removido com sucesso.")

            return True

        except IOError as ioerr:
            self.logger.error(f"Falha ao reconstruir a pasta. Erro: {ioerr}.")
            return False