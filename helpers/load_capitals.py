import httpx
import json

def load_capitals(file_path='json/capitals.json'):
    url = 'https://restcountries.com/v3.1/all?fields=name,flags,capital'

    with httpx.Client() as client:
        response = client.get(url)
        countries = response.json()

    capitals = {
        c['name']['common']: (c['capital'][0] if c.get('capital') else "Sem capital")
        for c in countries
}

    # Salva no arquivo JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(capitals, f, ensure_ascii=False, indent=4)

    print(f"✅ Capitais salvas em {file_path}!")


# Executar a função
load_capitals()
