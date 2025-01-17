# Exemplo de chamada
# from elfs.tools import collection_tls
#
# collection = collection_tls.CollectionEditor()
# collection.construir_colecao()

import os
import shutil
import logging
import pandas as pd

class CollectionEditor:
    def __init__(self):
        self._configure_logger()
        self.directory_domain = os.path.join("datacollection", "csv")

    def _configure_logger(self):
        """
        Configura o logger para registro das operações executadas.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _merge_csvs(self):
        """
        Mescla todos os CSVs temporários em único arquivo final, na ordem específica:
        1. zapimoveis_col.csv
        2. vivareal_col.csv
        3. olx_col.csv
        """

        try:
            df_list = []

            # Ordem específica dos arquivos.
            # Tem que ser nesta ordem para manter as colunas organizadas
            arquivos_em_ordem = ["vivareal_col.csv", "zapimoveis_col.csv", "olx_col.csv"]

            # Percorre a ordem especificada
            for arquivo_base in arquivos_em_ordem:
                caminho_arquivo = os.path.join(self.directory_domain, arquivo_base)
                if os.path.exists(caminho_arquivo):
                    df_temp = pd.read_csv(caminho_arquivo)
                    df_list.append(df_temp)
                else:
                    self.logger.warning(f"Arquivo {arquivo_base} não encontrado no diretório.")

            # Concatena todos os DataFrames, alinhando pelas colunas
            if df_list:
                df_final = pd.concat(df_list, axis=0, ignore_index=True, sort=False)
                filename = os.path.join(self.directory_domain, "collection.csv")
                df_final.to_csv(filename, index=False, encoding='utf-8')
                self.logger.info(f"Arquivo CSV final 'collection.csv' salvo com sucesso.")
            else:
                self.logger.warning("Nenhum arquivo CSV foi encontrado ou processado.")

        except Exception as e:
            self.logger.error(f"Erro ao mesclar os arquivos CSV: {e}")

    def normaliza_header(self,
                         padrao='ca'):
        """
        Normaliza a coelção para Caixa alta. Facilita a padronização da pesquisa posteriormente.
        :param padrao: 'ca' CAIXA ALTA. 'cb' caixa baixa.
        :return:
        """

        file_path = os.path.join(self.directory_domain, "collection.csv")

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)

                if padrao == 'ca':
                    df.columns = [col.upper() for col in df.columns]
                elif padrao == 'cb':
                    df.columns = [col.lower() for col in df.columns]

                df.to_csv(file_path, index=False)
                self.logger.info(f"Coleção resolvida com sucesso. Títulos em {padrao} (padrão de escrita).")
            except IOError as ioerr:
                self.logger.error(f"Erro ao nomalizar as colunas. {ioerr}")
            return False
        else:
            self.logger.error(f"Arquivo não existente.")
            return False

    def traduzir_olx(self):
        """
        Traduz as colunas da tabela OLX para normalizar os títulos.
        :return:
        """

        file_path = os.path.join(self.directory_domain, "olx_col.csv")

        translation_dict = {
            'Elevador': 'ELEVATOR',
            'Piscina': 'POOL',
            'Ar condicionado': 'AIR_CONDITIONING',
            'Churrasqueira': 'BARBECUE_GRILL',
            'Condomínio fechado': 'GATED_COMMUNITY',
            'Permitido animais': 'PETS_ALLOWED',
            'Academia': 'GYM',
            'Portaria': 'RECEPTION',
            'Salão de festas': 'PARTY_HALL',
            'Armários no quarto': 'BUILTIN_WARDROBE',
            'Armários na cozinha': 'KITCHEN_CABINETS',
            'Área de serviço': 'SERVICE_AREA',
            'Varanda': 'BALCONY',
            'Mobiliado': 'FURNISHED',
            'Segurança 24h': 'SECURITY_24_HOURS',
            'Quarto de serviço': 'SERVICE_ROOM'
        }

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                df.columns = [translation_dict.get(col, col) for col in df.columns]

                df.to_csv(file_path, index=False)

                self.logger.info(f"Tradução realizada com sucesso do arquivo OLX_COL.CSV.")
                return True

            except IOError as ioerr:
                self.logger.error(f"Erro ao traduzir colunas do CSV OLX: {ioerr}")
                return False
        else:
            self.logger.error(f"Arquivo não existente.")
            return False

    def resolve_zona_bairro(self,
                            remove_null = False,
                            padrao = None):
        """
        Resolve o problema de zonas do bairro.
        :param remove_null: Remove as entradas que tenham ZONA == NULL.
        :return: Dataset atualizado
        """

        file_path = os.path.join(self.directory_domain, "collection.csv")

        df = pd.read_csv(file_path)
        df.columns = [col.upper() for col in df.columns]

        mapping = df.dropna(subset=['ZONE', 'NEIGHBORHOOD']).set_index('NEIGHBORHOOD')['ZONE'].to_dict()

        # Função para preencher ZONE com base no NEIGHBORHOOD
        def preencher_zone(row):
            if pd.isna(row['ZONE']) or row['ZONE'] == '':
                return mapping.get(row['NEIGHBORHOOD'], row['ZONE'])  # Procura no mapeamento
            return row['ZONE']  # Mantém o valor existente se não for vazio

        if os.path.exists(file_path):
            try:
                df['ZONE'] = df.apply(preencher_zone, axis=1)

                if remove_null:
                    df = df.dropna(subset=['ZONE'])

                if padrao == 'cb':
                    df.columns = [col.lower() for col in df.columns]

                df.to_csv(file_path, index=False)
                return True
            except IOError as ioerr:
                self.logger.error(f"Erro ao nomalizar as colunas. {ioerr}")
                return False
        else:
            self.logger.error(f"Arquivo não existente.")
            return False

    def _limpar_arquivos_csv(self,
                            delete = False):
        """
        Limpa os arquivos da pasta CSV.
        :param delete: Se delete for FALSE, os arquivos apenas serão movidos para uma pasta temporária, a ser ignorada na hora de carregar este arquivo para o git. Se for escolhida a opção de delete, os arquivos serão apagados do sistema.
        :return: TRUE | FALSE
        """
        temp_folder = os.path.join(self.directory_domain, "ignore")

        try:
            if delete is False:
                if not os.path.exists(temp_folder):
                    os.makedirs(temp_folder)

                for file_name in os.listdir(self.directory_domain):
                    file_path = os.path.join(self.directory_domain, file_name)

                    if file_name.endswith(".csv") and file_name != "collection.csv":
                        shutil.move(file_path, os.path.join(temp_folder, file_name))

                self.logger.info("Arquivos CSV foram movidos para a pasta temp com sucesso.")

            else:
                for file_name in os.listdir(self.directory_domain):
                    file_path = os.path.join(self.directory_domain, file_name)

                    if file_name.endswith(".csv") and file_name != "collection.csv":
                        os.remove(file_path)

                self.logger.info("Arquivos CSV foram apagados, exceto o collection.csv.")

            return True
        except IOError as ioerr:
            self.logger.error(f"Falha ao apagar ou mover arquivos. {ioerr}.")
            return False

    def _corrige_numero_float(self):

        try:
            file_path = os.path.join(self.directory_domain, 'collection.csv')
            df = pd.read_csv(file_path)

            # Listar as colunas que precisam ser convertidas
            columns_to_fix = ["IPTU", "MONTHLYCONDOFEE", "USABLEAREAS", "TOTALAREAS", "SUITES"]

            for column in columns_to_fix:
                if column in df.columns:
                    df[column] = df[column].fillna(0).astype(int)

            df.to_csv(file_path, index=False)
            self.logger.info("Ação executada com sucesso. Transformação float em número na tabela collection.csv.")

            return True
        except Exception as e:
            self.logger.error(f"Falha ao transformar float em número. {e}")
            return False

    def construir_colecao(self,
                          padrao_titulo = 'ca',
                          remover_zona_nula = False,
                          delete_prep_files = False):
        """
        Função que cria toda a coleção e aplica estilos
        :param padrao_titulo: 'ca' CAIXA ALTA. 'cb' caixa baixa. Ver função normaliza_header
        :param remover_zona_nula: Ver função resolve_zona_bairro
        :param delete_prep_files: Se TRUE apaga os demais arquivos CSV de praparo da pasta CSV. Caso contrário (FALSE) apenas move para pasta temporária dentro do diretório. Ver _limpar_arquivos_csv. Padrão FALSE.
        :return: Dataset criado
        """

        try:
            # Primeira parte: Traduz OLX se existir
            self.traduzir_olx()
            self.logger.info("Ação executada com sucesso. Tradução OLX feita com sucesso.")
        except Exception as e:
            self.logger.error(f"Falha ao traduzir arquivo OLX. {e}")

        try:
            # Segunda parte: Criar a coleção usando merge
            self._merge_csvs()
            self.logger.info("Ação executada com sucesso. Merge dos CSVs.")
        except Exception as e:
            self.logger.error(f"Falha ao fazer merge CSV. {e}")

        try:
            # Terceira parte: Normalizar cabeçalho
            self.logger.debug(f"padrao_titulo {padrao_titulo}")
            self.normaliza_header(padrao = padrao_titulo)
            self.logger.info("Ação executada com sucesso. Normalização de cabeçalho.")
        except Exception as e:
            self.logger.error(f"Falha ao normalizar cabeçalhos. {e}")

        try:
            # Quarta parte: Resolve questão de bairros faltantes.
            # Se a opção remover_zona_nula for TRUE, ele também elimina as linhas que apresentam 'zona' == NULL
            self.logger.debug(f"remover_zona_nula {remover_zona_nula}")
            self.resolve_zona_bairro(
                                        remove_null=remover_zona_nula,
                                        padrao=padrao_titulo)
            self.logger.info("Ação executada com sucesso. Bairros e zonas resolvidos.")
        except Exception as e:
            self.logger.error(f"Falha ao resolver zonas e bairros. {e}")

        try:
            # Quinta parte: Remover arquivos de preparo.
            self.logger.debug(f"delete_prep_files {delete_prep_files}")
            self._limpar_arquivos_csv(delete=delete_prep_files)
            self.logger.info("Ação executada com sucesso. Arquivos temporários removidos ou remanejados.")
        except Exception as e:
            self.logger.error(f"Falha ao resolver zonas e bairros. {e}")

        # Sexta parte: Resolve número float.
        # Não precisa estar dentro de try/except porque já tem isso na função principal
        self._corrige_numero_float()