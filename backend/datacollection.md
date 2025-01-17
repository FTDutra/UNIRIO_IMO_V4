## Primeira parte: construção das bases
A **construção das bases** depende de ter o conjunto de dados ```raw``` já resolvidos. Este conjunto não será disponibilizado no git em função do ```.gitignore```, para ter acesso só através do drive do grupo ou conjunto RAR.

É possível criar a pasta ```raw``` usando os scripts da pasta ```scraper```, mas estes não estão implementados em nenhuma super-classe, sendo necessário rodar manualmente cada um deles.

## Segunda parte: construção dos arquivos CSVs temporários

Esta parte depende dos scripts localizados no diretório ```elfs.splitters```. Os splitters são chamados para efetivamente cortar os arquivos ```.json``` criados na **ETAPA 1**.

Não existe super-classe para eles, tem que ser chamado manualmente.

---
### Usando o splitter ```olx_spt```
```python
from elfs.splitters import olx_spt
olxspt = olx_spt.OlxSplitter()
```

### Usando o splitter ```vivareal_spt```
```python
from elfs.splitters import vivareal_spt
vivaspt = vivareal_spt.VivarealSplitter()
```

### Usando o splitter ```zapimoveis_spt```
```python
from elfs.splitters import zapimoveis_spt
zapimoveisspt = zapimoveis_spt.ZapimoveisSplitter()
```
---

Observe que o script ```zapimoveis``` depende de uma API externa. O script ```vivareal``` espera um arquivo .har extraído diretamente do painel ```NETWORK -> FETCH/XHR```.

Recomendo ver o ```splitter``` desejado para tirar eventuais dúvidas de como funciona.

## Terceira parte: construção da pasta ```DATA```

Para criar o conjunto de dados que irá ser compilado na pasta ```data```, é necessário rodar o script ```builders.py```.

A construção da pasta ```csv``` é feita usando os construtores disponíveis na pasta ```elf/builders```. O arquivo ```builders.py``` possui instruções de como montar cada um dos construtores.

---

### Usando o construtor ```builders.py```

Exemplo de chamada:
```python
from elfs.builders import builders

builder = builders.Builders()
builder.executar_builder(
    builder="",
    action="",
    delete_after=False)
```

Atenção que ele recebe os seguintes parâmetros:
```
:param builder: Pode ser 'zapimoveis', 'vivareal', 'olx'.
:param action: Define a ação que será feita. Por padrão é [3]. Cria o csv temporario e cria o arquivo final na pasta 'csv'
:param delete_after: Define se, após a execução, o arquivo temporário será deletado. Por padrão True.
:return: True | False
```

Uma vez executado ele irá criar a pasta ```csv``` e criar o conteúdo interno que será usado posteriormente.

---