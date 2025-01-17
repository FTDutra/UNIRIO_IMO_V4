import os
import csv
import logging
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt
from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor

class ReportTools:
    def __init__(self):
        self._configure_logger()

        # Instância do collection, para pegar as informações
        self.path = os.path.join("datacollection", "csv")
        self.data = os.path.join("datacollection", "csv", "collection.csv")
        self.data_code = os.path.join("datacollection", "csv", "collection_adj.csv")
        self.data_code_aggr = os.path.join("datacollection", "csv", "collection_adj_aggr.csv")

        # Caminho dos reports
        self.report_folder = os.path.join("report")
        self.report_folder_texts = os.path.join("report", "txts")
        self.report_folder_images = os.path.join("report", "images")

        # Cria os diretórios, se não existir
        os.makedirs(self.report_folder, exist_ok=True)
        os.makedirs(self.report_folder_texts, exist_ok=True)
        os.makedirs(self.report_folder_images, exist_ok=True)

    def _configure_logger(self):
        """
        Configura o logger para registro das operações executadas.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def correcao_entradas(self):
        """
        Corrige as entradas para eliminar o campo TYPE. Corrige também os campos OBJT -> INT
        Gera relatório ao final.
        :return: 
        """
        try:
            df = pd.read_csv(self.data)

            df = df.drop(columns=['TYPE'])

            df = df.map(lambda x: 6 if isinstance(x, str) and "5 ou mais" in x else x)
            df['PARKINGSPACES'] = df['PARKINGSPACES'].fillna(0)
            df['STREET'] = df['STREET'].fillna("")
            df = df.map(lambda x: True if x == "True" else (False if pd.isnull(x) else x))

            df['PARKINGSPACES'] = pd.to_numeric(df['PARKINGSPACES'], errors='coerce', downcast='integer')
            df['BATHROOMS'] = pd.to_numeric(df['BATHROOMS'], errors='coerce', downcast='integer')
            df['BEDROOMS'] = pd.to_numeric(df['BEDROOMS'], errors='coerce', downcast='integer')

            df.to_csv(self.data_code, index=False)

            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_rows', None)

            output_txt = os.path.join(self.report_folder_texts, "colunas_tipos_dados_adjs.txt")
            with open(output_txt, 'w') as f:
                f.write(str(df.dtypes))

            return True
        except Exception as e:
            self.logger.error(f"Erro ao manipular as colunas: {e}")
            return False

    def ajusta_csv_codigo(self):
        """
        Necessário para transformar as colunas categóricas em código, permitindo posterior conferência de correlação e possível treinamento.
        :return: CSV dataset
        """

        try:
            df = pd.read_csv(self.data_code)

            df['ZONE_CODE'] = df['ZONE'].astype('category').cat.codes + 1
            df['NEIGHBORHOOD_CODE'] = df['NEIGHBORHOOD'].astype('category').cat.codes + 1

            zone_index = df.columns.get_loc('ZONE') + 1
            neighborhood_index = df.columns.get_loc('NEIGHBORHOOD') + 1

            cols = [col for col in df.columns]
            df = df[['ZONE_CODE', 'NEIGHBORHOOD_CODE'] + cols]

            df = df.loc[:, ~df.columns.duplicated()]

            df.to_csv(self.data_code, index=False)
            self.logger.info(f"CODIFICAÇÃO realizada com sucesso.")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao CODIFICAR as colunas: {e}")
            return False

    def fix_aggr(self):

        def agrupar_colunas(df, categorias):

            df_agrupado = pd.DataFrame()

            for categoria, palavras in categorias.items():
                colunas = [coluna for coluna in df.columns if coluna in palavras]
                if colunas:
                    df_agrupado[categoria] = df[colunas].any(axis=1)
                    df = df.drop(columns=colunas)

            colunas_nao_agrupadas = [coluna for coluna in df.columns]
            df_agrupado = pd.concat([df_agrupado, df[colunas_nao_agrupadas]], axis=1)

            return df_agrupado

        categorias = {
            "FURNISHED":
                ["FURNISHED", "KITCHEN_CABINETS", "BATHROOM_CABINETS"],
            "GOURMET_SPACE": ["GOURMET_SPACE", "GOURMET_BALCONY", "GOURMET_KITCHEN", "BUILTIN_WARDROBE"],
            "KITCHEN": ["KITCHEN", "AMERICAN_KITCHEN"],
            "DRESS_ROOM": ["DRESS_ROOM", "CLOSET"],
            "BATHROOMS": ["BATHROOMS", "BATHTUB", "LAVABO"],
            "BALCONY":
                ["BALCONY", "WALL_BALCONY"],
            "SPORTS_COURT":
                ["SPORTS_COURT", "FOOTBALL_FIELD", "TENNIS_COURT", "INDOOR_SOCCER", "SKATE_LANE", "GOLF_FIELD",
                 "FITNESS_ROOM", "GYM", "SQUASH"],
            "FOOD_COURT":
                ["BARBECUE_GRILL", "RESTAURANT", "PIZZA_OVEN", "BAR", "COFFEE_SHOP"],
            "RECREATION_AREA":
                ["RECREATION_AREA", "ADULT_GAME_ROOM", "HOT_TUB", "AQUARIUM", "GAMES_ROOM", "TOYS_PLACE", "SAND_PIT",
                 "YOUTH_GAME_ROOM", "PLAYGROUND", "TEEN_SPACE", "PARTY_HALL"],
            "REST_AREAS":
                ["SPA", "SAUNA", "ZEN_SPACE", "MASSAGE_ROOM", "LIBRARY", "SOLARIUM", "BEAUTY_CENTER", "MASSAGE"],
            "POOL":
                ["POOL", "HEATED_POOL", "POOL_BAR", "COVERED_POOL", "WHIRLPOOL", "SEMI_OLYMPIC_POOL", "PRIVATE_POOL",
                 "REFLECTING_POOL", "CHILDRENS_POOL", "ADULT_POOL"],
            "SAFETY":
                ["ARMORED_SECURITY_CABIN", "SAFETY_CIRCUIT", "ALARM_SYSTEM", "SECURITY_CAMERA", "SECURITY_24_HOURS",
                 "WATCHMAN", "SECURITY_CABIN", "PATROL", "DEPOSIT", "INTERCOM", "CONCIERGE_24H", "ELETRONIC_GATE",
                 "RECEPTION", "DIGITAL_LOCKER", "ELECTRONIC_GATE", "GATED_COMMUNITY", "FENCE"],
            "VIEW":
                ["SEA_VIEW", "MOUNTAIN_VIEW", "PANORAMIC_VIEW", "EXTERIOR_VIEW", "LAKE_VIEW"],
            "ACCESSIBILITY":
                ["CHILDREN_CARE", "PAVED_STREET", "DISABLED_ACCESS"],
            "WORK_AREAS":
                ["COWORKING", "HOME_OFFICE", "MEETING_ROOM", "COVENTION_HALL"],
            "GARAGE":
                ["PARKING", "GARAGE", "GARAGE_BAND", "VALET_PARKING", "GUEST_PARKING"],
            "SUSTAINABILITY":
                ["SOLAR_ENERGY", "ECO_GARBAGE_COLLECTOR", "ECO_CONDOMINIUM", "NATURAL_VENTILATION", "BYCICLES_PLACE",
                 "SMART_APARTMENT", "SMART_CONDOMINIUM", "ELETRIC_CHARGER", "VEGETABLE_GARDEN", "BICYCLES_PLACE"],
            "OUTDOOR_AREAS":
                ["BACKYARD", "GREEN_SPACE", "FRUIT_TREES", "LAKE", "RIVER", "POMAR",
                 "TREE_CLIMBING", "MARINA", "SQUARE", "REDARIO", "ORCHID_PLACE"],
            "PET_FRIENDLY":
                ["PETS_ALLOWED", "PET_SPACE", "DOG_KENNEL"],
            "MID_END_APARTMENT_AMENITIES":
                ["COLD_FLOOR", "EMPLOYEE_DEPENDENCY", "SERVICE_BATHROOM", "AIR_CONDITIONING"],
            "HIGH_END_APARTMENT_AMENITIES":
                ["LARGE_KITCHEN", "LARGE_WINDOW", "LARGE_ROOM", "SOUNDPROOFING", "FIREPLACE", "THERMAL_INSULATION",
                 "HEATING"],
            "HIGH_END_CONDO_AMENITIES":
                ["SERVICE_ENTRANCE", "ENTRANCE_HALL", "HELIPAD", "HOME_CINEMA", "CINEMA", "HIKING_TRAIL",
                 "SOUNDPROOFING", "ELECTRIC_GENERATOR", "STORES"]
        }

        caminho_csv_original = self.data_code

        df = pd.read_csv(caminho_csv_original)

        df_agrupado = agrupar_colunas(df, categorias)

        df_agrupado = df_agrupado.drop(columns=[
            "SLAB", "PLATED_GAS", "FULL_FLOOR", "BLINDEX_BOX", "WOOD_FLOOR", "BEDROOM_WARDROBE", "GAS_SHOWER",
            "ALUMINUM_WINDOW", "INTEGRATED_ENVIRONMENTS", "PORCELAIN", "PAY_PER_USE_SERVICES", "SERVICE_ROOM", "SANCA",
            "GRASS", "HIGH_CEILING_HEIGHT", "SIDE_ENTRANCE", "PLANNED_FURNITURE", "PANTRY", "SMALL_ROOM",
            "REVERSIBLE_ROOM", "COPA", "COOKER", "WATER_TANK", "DIVIDERS", "FREEZER", "FULL_CABLING", "CARETAKER",
            "DECK", "HALF_FLOOR", "STAIR", "WELL", "ARTESIAN_WELL", "LAMINATED_FLOOR", "GLASS_WALL", "CORNER_PROPERTY",
            "WALLS_GRIDS", "GEMINADA", "ADMINISTRATION", "VINYL_FLOOR", "LAND", "DRYWALL", "BURNT_CEMENT", "MEZZANINE",
            "PASTURE", "RAISED_FLOOR", "EDICULE", "HEADQUARTERS", "BACKGROUND_HOUSE",
            "NEAR_SHOPPING_CENTER_2", "DRESS_ROOM2", "DINNER_ROOM", "CABLE_TV", "NUMBER_OF_FLOORS", "INTERNET_ACCESS"
        ])

        df_agrupado["YEARLY_EXPENSES"] = df_agrupado["IPTU"] + (df_agrupado["MONTHLYCONDOFEE"] * 12)

        df_agrupado = df_agrupado[df_agrupado["PRICE"] >= 99999]

        df_agrupado = df_agrupado.drop(columns=["IPTU", "MONTHLYCONDOFEE"])

        caminho_csv_agrupado = self.data_code_aggr

        df_agrupado.to_csv(caminho_csv_agrupado, index=False)

        print(f"Arquivo agrupado salvo em: {caminho_csv_agrupado}")

    import pandas as pd
    import os
    from statsmodels.tools.tools import add_constant
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from tqdm import tqdm

    def fix_multicol(self):
        file_path = self.data_code_aggr
        df = pd.read_csv(file_path)

        # Salvar as colunas que não serão consideradas no cálculo da multicolinearidade
        cols_to_keep = ['ZO2NE', 'NEIGHBORHOOD', 'STREET']
        df_for_multicol = df.drop(columns=cols_to_keep)  # Ignorar as colunas para o cálculo da multicolinearidade

        # Mapear valores booleanos para 1/0
        df_for_multicol = df_for_multicol.map(lambda x: 1 if x is True else (0 if x is False else x))

        # Converter todas as colunas para numéricas
        df_for_multicol = df_for_multicol.apply(pd.to_numeric, errors='coerce')

        # Calcular a matriz de correlação
        correlation_matrix = df_for_multicol.corr()

        # Função para calcular o VIF (Variance Inflation Factor)
        def calcular_vif(df):
            # Adicionar uma constante (intercepto) ao DataFrame
            df_const = add_constant(df)

            # Calculando o VIF para cada variável com barra de progresso
            vif_data = pd.DataFrame()
            vif_data["Variável"] = df_const.columns

            # Barra de progresso para o cálculo do VIF
            vif_data["VIF"] = [
                variance_inflation_factor(df_const.values, i) for i in
                tqdm(range(df_const.shape[1]), desc="Calculando VIF")
            ]

            return vif_data

        # Calcular o VIF com barra de progresso
        vif_resultado = calcular_vif(df_for_multicol)

        # Identificar variáveis com VIF maior que 5 (indicando multicolinearidade)
        variaveis_com_multicolinearidade = vif_resultado[vif_resultado["VIF"] > 5]

        # Excluir variáveis com VIF > 5
        variaveis_a_excluir = variaveis_com_multicolinearidade["Variável"].tolist()
        # variaveis_a_excluir.remove("const")

        # Excluir as variáveis do DataFrame original para o cálculo
        df_reduzido = df_for_multicol.drop(columns=variaveis_a_excluir)

        # Adicionar as colunas originais de volta
        df_reduzido[cols_to_keep] = df[cols_to_keep]

        # Salvar o CSV final
        output_file_path = os.path.join(self.path, 'collection_wt_multicol.csv')
        df_reduzido.to_csv(output_file_path, index=False)

        # Criar o relatório
        relatorio = []

        # Barra de progresso para a geração do relatório
        for var in tqdm(variaveis_com_multicolinearidade["Variável"], desc="Gerando Relatório"):
            # Adicionar a variável ao relatório
            relatorio.append(f"Variável com VIF > 5: {var}")

            # Ignorar a coluna 'const' na matriz de correlação
            if var in correlation_matrix.columns:
                correlacoes_alto = correlation_matrix[var][abs(correlation_matrix[var]) > 0.8]

                # Excluir a própria variável da lista de correlações
                correlacoes_alto = correlacoes_alto[correlacoes_alto.index != var]

                if len(correlacoes_alto) > 0:
                    relatorio.append(f"  - Variáveis com correlação > 0.8 com {var}:")
                    for correl in correlacoes_alto.index:
                        relatorio.append(f"    - {correl} (correlação = {correlacoes_alto[correl]:.2f})")
                else:
                    relatorio.append(f"  - Nenhuma variável com correlação > 0.8 com {var}.")
            else:
                relatorio.append(f"  - Variável {var} não encontrada na matriz de correlação.")

        # Salvar o relatório de multicolinearidade
        output_report_path = os.path.join(self.report_folder_texts, 'relatorio_multicolinearidade.txt')
        with open(output_report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(relatorio))

    def clean_outlier(self):
        input_file = os.path.join("datacollection", "csv", "collection_wt_multicol.csv")
        output_cleaned = os.path.join("datacollection", "csv", "cleaned_data.csv")
        output_outliers = os.path.join("datacollection", "csv", "outliers.csv")

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"O arquivo {input_file} não foi encontrado.")

        # Carregar os dados
        data = pd.read_csv(input_file)

        # Eliminar entradas com PRICE < 100000
        data = data[data["PRICE"] >= 99999]

        # Identificar outliers usando o IQR de forma consistente
        def identify_outliers(df):
            # Copiar o dataset original
            cleaned_data = df.copy()

            # DataFrame para armazenar os outliers
            outliers = pd.DataFrame(columns=df.columns)

            # Avaliar os outliers de uma vez para todas as colunas numéricas
            for column in df.select_dtypes(include='number').columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # Identificar outliers na coluna atual
                column_outliers = ~((df[column] >= lower_bound) & (df[column] <= upper_bound))

                # Adicionar os outliers da coluna ao DataFrame de outliers
                outliers = pd.concat([outliers, df[column_outliers]])

                # Remover os outliers do dataset limpo
                cleaned_data = cleaned_data[~column_outliers]

            # Remover duplicatas dos outliers
            outliers = outliers.drop_duplicates()

            return cleaned_data, outliers

        # Separar dados limpos e outliers
        cleaned_data, outliers = identify_outliers(data)

        # Salvar os resultados
        cleaned_data.to_csv(output_cleaned, index=False)
        outliers.to_csv(output_outliers, index=False)

        print(f"Dados limpos salvos em: {output_cleaned}")
        print(f"Outliers salvos em: {output_outliers}")
