# -------------------------------------------------------------------------------
# O scraper faz todas as requisições para as páginas para montar o datacollection
# -------------------------------------------------------------------------------
# Foi criado um scraper específico para a OLX Imóveis e para o Zap Imóveis
# A base Viva real teve que ser recolhida manualmente, em razão da forma que o
#   site carrega os dados.
# -------------------------------------------------------------------------------
# Uma vez feita a coleta, os dados passarão pelos splitters, que vão se ocupar em
#   separar cada imóvel.
# Depois do splitter, passarão pelo glue, que vai montar o dataset final de cada
#   base e o dataset compilado.
# -------------------------------------------------------------------------------

# Trecho que chama e faz o levantamento dos dados da OLX na seção de imóveis
from scraper import olx_scp
OLX = olx_scp.OlxDataCollector()
OLX.collect_data()

# Trecho que chama e faz o levantamento dos dados do Zap Imóveis
from scraper import zapimoveis_scp
ZAPImoveis = zapimoveis_scp.ZapImoveisDataCollector()
ZAPImoveis.collect_data()
