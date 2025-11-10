import json
from deep_translator import GoogleTranslator

def traduzir(texto):
    if texto.lower() in ["sem capital", "sem moeda"]:
        return texto  # mantém
    return GoogleTranslator(source="auto", target="pt").translate(texto)

with open("json/capitals.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

novo = {}

for pais, info in dados.items():
    print(f"Traduzindo: {pais}")

    pais_pt = traduzir(pais)
    capital_pt = traduzir(info["capital"])
    moeda_pt = traduzir(info["currency"])

    novo[pais_pt] = {
        "capital": capital_pt,
        "moeda": moeda_pt
    }

with open("json/capitais.json", "w", encoding="utf-8") as f:
    json.dump(novo, f, ensure_ascii=False, indent=4)

print("✅ Tradução concluída! Arquivo gerado: capitais_pt.json")
