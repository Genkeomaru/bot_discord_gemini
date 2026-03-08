import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega a sua chave do .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Perguntando ao Google quais modelos você pode usar...")
print("-" * 50)

# Lista todos os modelos e filtra os que servem para gerar texto (generateContent)
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # Pega apenas o nome limpo após a barra (ex: tira o 'models/')
            nome_limpo = m.name.split('/')[-1]
            print(f"Nome exato para usar: {nome_limpo}")
except Exception as e:
    print(f"Erro ao consultar a API: {e}")
        
print("-" * 50)
print("Fim da lista.")