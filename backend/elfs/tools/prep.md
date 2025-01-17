## Prep_tls

O arquivo ```prep_tls.py``` tem a única função de desmembrar o aquivo ```datacollection\csv\collection.csv``` --- ou outro passado no momento do chamamento --- para resguardar (**x**)% (padrão 10%) dos dados para validação posterior.

Exemplo de chamada:
```python
from elfs.tools import prep_tls
```

Informações padrões da chamada:
```python
self.path = directory_path or os.path.join("datacollection", "csv")
file_name = file_name or "collection.csv"
self.data = os.path.join(self.path, file_name)
self.validate = (validate_p / 100) if validate_p is not None else 0.1
```