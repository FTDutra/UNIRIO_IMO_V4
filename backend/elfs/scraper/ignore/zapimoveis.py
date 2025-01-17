import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()
api_key = os.getenv("ZAPIMOVEIS_APIFY_API_KEY")

if not api_key:
    raise ValueError("A chave da API não foi definida. Configure a variável de ambiente 'APIFY_API_KEY'.")

client = ApifyClient(api_key)

output_dir = "datacollection/vivareal"
os.makedirs(output_dir, exist_ok=True)

for page in range(1, 101):
    try:
        run_input = {
            "type": "SALE",
            "city": "Rio de Janeiro",
            "state": "Rio de Janeiro",
            "unitType": "APARTMENT",
            "unitUsage": "RESIDENTIAL",
            "page": page
        }

        run = client.actor("1WyG7WWJM9Qjhmh1y").call(run_input=run_input)

        results = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        file_name = os.path.join(output_dir, f"{page}.json")
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print(f"Página {page} salva em: {file_name}")
    except Exception as e:
        print(f"Erro ao processar a página {page}: {e}")