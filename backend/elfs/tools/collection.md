# Detalhes do código que cuida da Coleção
Esta parte é diretamente relacionada ao script ```collection_tls.py``` localizado na pasta ```elfs.tools```.

Primeiro, exemplo de chamada do script:
```python
from elfs.tools import collection_tls

collection = collection_tls.CollectionEditor()
```

Todo o script recebe como parâmetros:
```python
self.directory_domain = os.path.join("datacollection", "csv")
file_path = os.path.join(self.directory_domain, "collection.csv")
```

A chamada ```normaliza_header``` normaliza a coelção para Caixa alta. Facilita a padronização da pesquisa posteriormente. Tem como parâmetro:
```python
padrao: 'ca' CAIXA ALTA. 'cb' caixa baixa.
```

A chamada ```traduzir_olx``` traduz as colunas da tabela OLX para normalizar os títulos. São feitas as seguintes traduções:

```python
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
```

A chamada ```resolve_zona_bairro``` cuida em localizar os bairros que possuem ZONA já populada e, olhando estes, buscar os bairros que estão sem ZONA para popular o campo.

Recebe como parâmetros:
```
:param remove_null: Remove as entradas que tenham ZONA == NULL.
:return: Dataset atualizado
```

A chamada ```construir_colecao``` é a mais importante, uma vez que é ela quem vai criar o arquivo final ```collection.csv```. Recebe os seguintes parâmetros:
```python
padrao_titulo = 'ca',
remover_zona_nula = False,
delete_prep_files = False
```

Sendo:
```
Função que cria toda a coleção e aplica estilos
:param padrao_titulo: 'ca' CAIXA ALTA. 'cb' caixa baixa. Ver função normaliza_header
:param remover_zona_nula: Ver função resolve_zona_bairro
:param delete_prep_files: Se TRUE apaga os demais arquivos CSV de praparo da pasta CSV. Caso contrário (FALSE) apenas move para pasta temporária dentro do diretório. Ver _limpar_arquivos_csv. Padrão FALSE.
:return: Dataset criado
```
